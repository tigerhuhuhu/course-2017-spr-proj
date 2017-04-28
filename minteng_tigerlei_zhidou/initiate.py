import sys
import os 
import importlib
import json
import argparse
import prov.model

parser = argparse.ArgumentParser()
parser.add_argument("contributor_folder")
parser.add_argument("-t", "--trial", help="run all algorithms in trial mode", action="store_true")
args = parser.parse_args()
# Extract the algorithm classes from the modules in the
# subdirectory specified on the command line
os.chdir("..")
# print(os.getcwd())
path = args.contributor_folder
algorithms = []
for file in os.listdir(path):
    # for file in f:
    if file.split(".")[-1] == "py":
    	if file.split(".")[0] == "initiate":
    		pass
    	else:
    		# print(file)
	        name_module = ".".join(file.split(".")[0:-1])
	        # print(name_module)
	        module = importlib.import_module(name_module)
	        algorithms.append(module.__dict__[name_module])

# Create an ordering of the algorithms based on the data
# sets that they read and write.
datasets = set()
ordered = []
while len(algorithms) > 0:
    for i in range(0,len(algorithms)):
        if set(algorithms[i].reads).issubset(datasets):
            datasets = datasets | set(algorithms[i].writes)
            ordered.append(algorithms[i])
            del algorithms[i]
            break

# Execute the algorithms in order.
provenance = prov.model.ProvDocument()
for algorithm in ordered:
    algorithm.execute(trial=args.trial)
    provenance = algorithm.provenance(provenance)

# Display a provenance record of the overall execution process.
print(provenance.get_provn())

# Render the provenance document as an interactive graph.
prov_json = json.loads(provenance.serialize())
import protoql
agents = [[a] for a in prov_json['agent']]
entities = [[e] for e in prov_json['entity']]
activities = [[v] for v in prov_json['activity']]
wasAssociatedWith = [(v['prov:activity'], v['prov:agent'], 'wasAssociatedWith') for v in prov_json['wasAssociatedWith'].values()]
wasAttributedTo = [(v['prov:entity'], v['prov:agent'], 'wasAttributedTo') for v in prov_json['wasAttributedTo'].values()]
wasDerivedFrom = [(v['prov:usedEntity'], v['prov:generatedEntity'], 'wasDerivedFrom') for v in prov_json['wasDerivedFrom'].values()]
wasGeneratedBy = [(v['prov:entity'], v['prov:activity'], 'wasGeneratedBy') for v in prov_json['wasGeneratedBy'].values()]
used = [(v['prov:activity'], v['prov:entity'], 'used') for v in prov_json['used'].values()]
open('provenance.html', 'w').write(protoql.html("graph(" + str(entities + agents + activities) + ", " + str(wasAssociatedWith + wasAttributedTo + wasDerivedFrom + wasGeneratedBy + used) + ")"))

## eof