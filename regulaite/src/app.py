import argparse, json
from regulaite.orchestrator import Orchestrator

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default="example/demo")
    args=p.parse_args()
    print(json.dumps(Orchestrator(args.repo).run(),indent=2))

if __name__=="__main__": main()