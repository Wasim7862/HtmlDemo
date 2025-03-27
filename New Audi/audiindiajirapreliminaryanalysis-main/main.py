from LogHandler import LogHandler
from APIFunctions import APIFunctions


logger = LogHandler.get_logger('Main')
logger.propagate = False


if __name__ == '__main__':
    logger.info('Start')
    api_functions_object = APIFunctions()
    api_functions_object.get_Waiting_for_support_tickets()
    if APIFunctions.count_of_tickets == 0:
        logger.info('No tickets to process')
    else:
        logger.info('{0} tickets to process'.format(APIFunctions.count_of_tickets))
        api_functions_object.generate_Token()
        api_functions_object.perform_preliminary_analysis()
        api_functions_object.add_comment_in_jira()
        api_functions_object.change_ticket_status_to_inprogress()
        api_functions_object.change_ticket_assignee()
