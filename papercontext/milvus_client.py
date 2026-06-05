"""establishing connection to milvus"""
import logging
from pymilvus import connections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#connecting to milvus
def connect_to_milvus():
    try:
        connections.connect(
            alias="default",
            host="localhost",
            port="19530"
        )

        logger.info(
            "Connection established successfully to Milvus!"
        )

    except Exception as e:
        logger.exception(
            "Failed to connect to Milvus"
        )
        raise

if __name__ == "__main__":
    connect_to_milvus()


