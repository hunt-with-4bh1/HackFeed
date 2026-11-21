import logging
from core.pipeline import run_pipeline
from generators.render import render

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    data = run_pipeline()
    render(data)
    print(f"HackFeed updated: {data['total']} records; {data['last_run']['new_entries']} new this run.")
