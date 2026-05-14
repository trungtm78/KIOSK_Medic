from typing import Any, Dict
from ..servicelogs.servicelogger import logger


class KBService:
    def query(self, slots: Dict[str, Any]) -> Any:
        # Placeholder KB result based on a simple slot
        if 'service_name' in slots:
            data = {'checklist': ['CCCD', 'BHYT'], 'fee_estimate': '~200k', 'counter': 'Procedure Desk'}
        elif 'main_symptom' in slots:
            data = [{'dept': 'Internal Medicine', 'reason': 'General symptoms'}, {'dept': 'ENT', 'reason': 'Throat issues'}]
        else:
            data = {'info': 'KB default response'}
        logger.info(f"KB: query with slots {slots} -> {data}")
        return data

