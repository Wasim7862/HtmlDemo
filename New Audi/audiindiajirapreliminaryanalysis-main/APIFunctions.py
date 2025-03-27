import base64

import requests
import re
import Config
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from LogHandler import LogHandler

logger = LogHandler.get_logger('APIFunctions')


class APIFunctions():
    count_of_tickets = None
    tickets_lst = []
    preliminary_analysis_details = []
    cerence_api_token = None

    def get_Waiting_for_support_tickets(self):
        headers = {'Authorization': Config.JIRA_TOKEN}
        response = requests.get(Config.WAITING_FOR_SUPPORT_TICKETS_URI, headers=headers, verify=False)
        if response.status_code == 200:
            result = response.json()
            APIFunctions.count_of_tickets = result['total']
            for item in range(APIFunctions.count_of_tickets):
                ticket_record = dict()
                ticket_record['key'] = result['issues'][item]['key']
                description = result['issues'][item]['fields']['description']
                imeis = re.findall(r'\b[0-9]{15}\b', description)
                imeiList = []
                for imeiValue in imeis:
                    imeiList.append(imeiValue)
                imei = imeiList
                ticket_record['imei'] = imei
                try:
                    vins = re.findall(r'\b[A-Z0-9]{17}\b', description)
                    vin = vins[0]
                except:
                    vin = 'NA'
                    logger.info("VIN not present in ticket description")
                ticket_record['vin'] = vin
                APIFunctions.tickets_lst.append(ticket_record)
            logger.info('Jira tickets list:')
            for item in APIFunctions.tickets_lst:
                logger.info(item)
        else:
            logger.warning('API response code: {0}'.format(response.status_code))
            logger.warning(response.content)
            logger.warning(response.text)
            APIFunctions.count_of_tickets = 0


    def perform_preliminary_analysis(self):
        for item in APIFunctions.tickets_lst:
            logger.info(item)
            for imei in item['imei']:
                logger.info(imei)
                dict = APIFunctions.get_device_inventory_details(imei)
                if dict is None:
                    logger.error('No record found for IMEI: '+imei)
                elif dict['carId'] != 'NA' and dict['state'] == 'USER_MAPPED':
                    timestamp = APIFunctions.get_last_seen_details(dict['carId'], imei)
                    if timestamp == None:
                        dict['lastSeen'] = 'NA'
                    else:
                        dict['lastSeen'] = datetime.fromtimestamp(timestamp, timezone(timedelta(hours=5, minutes=30)))
                else:
                    dict['lastSeen'] = 'NA'

                if dict is None:
                    logger.error('No record found for IMEI: '+imei)
                elif dict['state'] == 'USER_MAPPED':
                    dict['status'] = APIFunctions.get_device_status(imei)
                    user_Details_dict = APIFunctions.get_user_details(imei)
                    dict['firstName'] = user_Details_dict['firstName']
                    dict['email'] = user_Details_dict['email']
                    dict['phone'] = user_Details_dict['phone']
                else:
                    dict['status'] = 'NA'
                    dict['firstName'] = 'NA'
                    dict['email'] = 'NA'
                    dict['phone'] = 'NA'
                dict['jiraTicket'] = item['key']
                APIFunctions.preliminary_analysis_details.append(dict)

    def generate_Token(self):
        headers = {'Content-Type': 'application/json', 'accept': 'application/json;charset=UTF-8'}
        data = '{  "loginType": 0,  "password": "Welcome@123",  "username": "akshay.somvanshi@cerence.com"}'
        response = requests.post(Config.TOKEN_URI, data=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            APIFunctions.cerence_api_token = 'Bearer '+ result['loginInfo']['tokenInfo']['accessToken']
            logger.info('Cerence Token generated.')
        else:
            logger.error('Unable to generate Cerence Token.')

    def get_device_inventory_details(imei):
        headers = {'Authorization': APIFunctions.cerence_api_token, 'accept': '*/*'}
        response = requests.get(Config.GET_DEVICE_DETAILS + imei, headers=headers)
        if response.status_code == 200:
            result = response.json()
            dict = {}
            dict['imei'] = result['imei']
            dict['state'] = result['state']
            dict['iccid'] = result['iccid']
            dict['deviceType'] = result['deviceType']
            dict['firmware'] = result['firmware']
            if result['vin']:
                dict['vin'] = result['vin']
            else:
                dict['vin'] = 'NA'
            if result['carId']:
                dict['carId'] = result['carId']
            else:
                dict['carId'] = 'NA'
            if result['ownerGroup']['name']:
                dict['dealerName'] = result['ownerGroup']['name']
            else:
                dict['dealerName'] = 'NA'
            if 'dealerCode' in result['ownerGroup']:
                dict['dealerCode'] = result['ownerGroup']['dealerCode']
            else:
                dict['dealerCode'] = 'NA'
            return dict
        else:
            dict = {}
            dict['imei'] = imei
            dict['state'] = 'NA'
            dict['iccid'] = 'NA'
            dict['deviceType'] = 'NA'
            dict['firmware'] = 'NA'
            dict['vin'] = 'NA'
            dict['carId'] = 'NA'
            dict['dealerName'] = 'NA'
            dict['dealerCode'] = 'NA'
            return dict

    def get_last_seen_details(carId, imei):
        headers = {'Authorization': APIFunctions.cerence_api_token, 'accept': 'application/json, text/plain, */*'}
        response = requests.get(Config.GET_LAST_SEEN_DETAILS + carId, headers=headers)
        if response.status_code == 200:
            result = response.json()
            logger.info('Last seen received for {0}'.format(imei))
            try:
                return result['telemetry']['timestamp']
            except:
                logger.info('Exception')
                return None
        else:
            return None

    def add_comment_in_jira(self):
        for item in APIFunctions.preliminary_analysis_details:
            logger.info('Preliminary analysis details for {0} are below'.format(item['jiraTicket']))
            logger.info(item)
            APIFunctions.add_comment_in_jira_ticket(item)

    def add_comment_in_jira_ticket(item):
        headers = {'Authorization': Config.JIRA_TOKEN, 'Content-Type': 'application/json', 'accept': 'application/json;charset=UTF-8'}
        comment = "Preliminary Analysis:\\nIMEI: {0}\\nICCID: {1}\\nDevice Type: {2}\\nState: {3}\\nStatus: {4}\\nVIN: {5}\\nCar Id: {6}\\nLast communication date of device in platform: {7}\\nDevice Firmware version: {8}\\nDealer name: {9}\\nDealer code: {10}\\nUser Name: {11}\\nUser phone: {12}\\nUser email: {13}".format(item['imei'], item['iccid'], item['deviceType'], item['state'], item['status'], item['vin'], item['carId'], item['lastSeen'], item['firmware'], item['dealerName'], item['dealerCode'], item['firstName'], item['email'], item['phone'])
        data = '{ "body": {"type": "doc", "version": 1, "content": [{"type": "paragraph","content": [{"text": '+'\"'+comment+'\",'+'"type": "text"} ]}]}, "properties": [{"key": "sd.public.comment","value": {"internal": true}}]}'
        response = requests.post(Config.ADD_COMMENT1+item['jiraTicket']+Config.ADD_COMMENT2, data=data, headers=headers, verify=False)
        if response.status_code == 201:
            logger.info('Preliminary analysis added in {0}.'.format(item['jiraTicket']))
        else:
            logger.error('Unable to add preliminary analysis in {0}. API response code is {1}'.format(item['jiraTicket'], response.status_code))
            logger.error(response.content)

    def change_ticket_status_to_inprogress(self):
        for item in APIFunctions.preliminary_analysis_details:
            headers = {'Authorization': Config.JIRA_TOKEN, 'Content-Type': 'application/json',
                   'accept': 'application/json;charset=UTF-8'}
            data = '{"transition":{"id":"891"}}'
            response = requests.post(Config.CHANGE_TICKET_STATUS1 + item['jiraTicket'] + Config.CHANGE_TICKET_STATUS2, data=data,
                                 headers=headers, verify=False)
            if response.status_code == 204:
                logger.info('Ticket status changes for {0}.'.format(item['jiraTicket']))
            else:
                logger.error('Unable to change ticket status of {0}. API response code is {1}'.format(item['jiraTicket'],
                                                                                                 response.status_code))
                logger.error(response.content)

    def change_ticket_assignee(self):
        for item in APIFunctions.preliminary_analysis_details:
            headers = {'Authorization': Config.JIRA_TOKEN, 'Content-Type': 'application/json',
                       'accept': 'application/json;charset=UTF-8'}
            data = '{"accountId": "62944ac6c3dffc0068f3c162"}'
            response = requests.put(Config.CHANGE_TICKET_ASSIGNEE1 + item['jiraTicket'] + Config.CHANGE_TICKET_ASSIGNEE2,
                                     data=data,
                                     headers=headers, verify=False)
            if response.status_code == 204:
                logger.info('Ticket assignee is changed for {0}.'.format(item['jiraTicket']))
            else:
                logger.error(
                    'Unable to change ticket assignee of {0}. API response code is {1}'.format(item['jiraTicket'],
                                                                                             response.status_code))
                logger.error(response.content)

    @classmethod
    def get_device_status(self, imei):
        headers = {'Authorization': APIFunctions.cerence_api_token, 'accept': 'application/json, text/plain, */*'}
        response = requests.get(Config.GET_DEVICE_STATUS1 + imei + Config.GET_DEVICE_STATUS2, headers=headers)
        if response.status_code == 200:
            result = response.json()
            logger.info('Device status received for {0}'.format(imei))
            try:
                return result['content'][0]['status']
            except:
                logger.info('Exception')
                return None
        else:
            return None

    @classmethod
    def get_user_details(self, imei):
        headers = {'Authorization': APIFunctions.cerence_api_token, 'accept': 'application/json, text/plain, */*'}
        response = requests.get(Config.GET_DEVICE_STATUS1 + imei + Config.GET_DEVICE_STATUS2, headers=headers)
        if response.status_code == 200:
            result = response.json()
            logger.info('User details received for {0}'.format(imei))
            try:
                return {'firstName': result['content'][0]['user']['firstName'], 'email': result['content'][0]['user']['email'], 'phone': result['content'][0]['user']['phone']}
            except:
                logger.info('Exception')
                return None
        else:
            return None
