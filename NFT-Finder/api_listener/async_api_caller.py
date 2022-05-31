import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
import requests
from retry import retry
from helpers.custom_exceptions import RequestFailedException
from helpers.add_extensions import SafeList, validate_activity

logger = logging.getLogger(__name__)
# in seconds
MAX_RETRIES = 3
REQUEST_TIMEOUT = 2
GOOD_STATUS_CODE = 200

@dataclass
class APICaller:
    """The class is needed for fetching data from Rarible API and convert it into 
    the form defined in schemas.py
    """
    start_with_item: str
    start_with_activity: str
    duration: int = 1
    from_date: datetime = field(default_factory=datetime.now)
    to_date: datetime = field(default_factory=datetime.now)
    blockchain_type: str = 'ETHEREUM'
    base_url = 'https://api.rarible.org/v0.1'
    BATCH_SIZE = 1000

    def form_dict(self) -> dict:
        from_date = self.from_date
        to_date = self.to_date
        date_unix_from = int(time.mktime(from_date.timetuple()))
        #date_unix_to = int(time.mktime(to_date.timetuple()))
        if self.start_with_item:
            return {
                "size": APICaller.BATCH_SIZE, 
                "lastUpdatedFrom": date_unix_from,
                "showDeleted": False,
                "continuation": self.start_with_item
                }
        else:
            return {
                "size": APICaller.BATCH_SIZE,
                "type": 'SELL',
                "showDeleted": False,
                "lastUpdatedFrom": date_unix_from
                }
    @retry(RequestFailedException, tries = MAX_RETRIES, delay = REQUEST_TIMEOUT)
    async def get_sell_activities(self) -> tuple[SafeList[str], str]:
        """Function forming requests for fetching User Sell Activities on the Rarible Market Platform
        Each sell activity corresponds to a NFT Item was sold, i.e. by combination of Ids {currency:token:tokenId},
        which are needed to get wider information set about the sold NFTs.

        API Docs: https://api.rarible.org/v0.1/doc#operation/getAllActivities

        Returns:
            list[str]: A tuple containing list of extracted NFT identificators and the continuation string
        """
        result = SafeList([])

        params = {
            # blockchains not specified -> all will be searched
            "type": 'SELL',
            "sort": 'LATEST_FIRST',
            "size": APICaller.BATCH_SIZE
        }

        if self.start_with_item:
            params["continuation"] = self.start_with_activity

        response = requests.get(self.base_url + '/activities/all', params = params)
        if response.status_code == GOOD_STATUS_CODE:
            response_json = response.json()

            if len(response_json['activities']):
                results = SafeList(filter(validate_activity, response_json['activities']))
                result = set([i['nft']['type']['itemId'] for i in results])
            else:
                logger.exception(RequestFailedException(response))
                
        return result, response_json['continuation']

    @retry(RequestFailedException, tries = MAX_RETRIES, delay = REQUEST_TIMEOUT)
    async def get_item_by_id(self, id: str) -> list[dict]:
        """Function forming and sending requests to the API: https://api.rarible.org/v0.1/doc#operation/getItemById

        Args:
            id (str): A NFT id, composed as the combination of blockchain Ids {currency:token:tokenId}

        Returns:
            list[dict]: A list containing a dictionary with corresponding NFT Information
        """
        result = SafeList([])
        response = requests.get(self.base_url + f'/items/{id}')
        if response.status_code == GOOD_STATUS_CODE:
            response_json = response.json()
            if response_json:
                result = response_json
        elif response.status_code == 404:
            logger.warning(f"Item with id {id} was not found.")
        else:
            logger.exception(RequestFailedException(response))

        return result