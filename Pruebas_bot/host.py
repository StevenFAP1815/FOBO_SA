import logging
import sys

from app import create_app


app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)
    

import sys
sys.dont_write_bytecode = True

    