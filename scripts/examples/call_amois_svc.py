#!/usr/bin/env python3

import os
import pprint

import requests

vr = {
    "singleNucleotideVariants": [
        {
            "confirmed": True,
            "gene": "EGFR",
            "oncominevariantclass": "Hotspot",
            "exon": "20",
            "function": "missense",
            "geneName": "",
            "chromosome": "chr7",
            "position": "55249071",
            "identifier": "COSM6240",
            "reference": "C",
            "alternative": "T",
            "filter": "PASS",
            "protein": "p.Thr790Met",
            "inclusion": True,
            "armSpecific": False
        },
        {
            "confirmed": True,
            "gene": "TP53",
            "oncominevariantclass": "Hotspot",
            "exon": "7",
            "function": "missense",
            "geneName": "",
            "chromosome": "chr17",
            "position": "7577538",
            "identifier": "COSM10662",
            "reference": "C",
            "alternative": "T",
            "filter": "PASS",
            "protein": "p.Arg248Gln",
            "inclusion": True,
            "armSpecific": False
        }
    ],
    "indels": [
        {
            "confirmed": True,
            "gene": "EGFR",
            "oncominevariantclass": "Hotspot",
            "exon": "19",
            "function": "nonframeshiftDeletion",
            "geneName": "",
            "chromosome": "chr7",
            "position": "55242465",
            "identifier": "COSM6223",
            "reference": "GGAATTAAGAGAAGC",
            "alternative": "-",
            "filter": "PASS",
            "protein": "p.Glu746_Ala750del",
            "inclusion": True,
            "armSpecific": False
        }
    ],
    "copyNumberVariants": [
        {
            "refCopyNumber": 2.0,
            "rawCopyNumber": 7.79,
            "copyNumber": 7.79,
            "confidenceInterval95percent": 8.40235,
            "confidenceInterval5percent": 7.22227,
            "confirmed": True,
            "gene": "EGFR",
            "oncominevariantclass": "Amplification",
            "exon": "",
            "function": "",
            "geneName": "",
            "chromosome": "chr7",
            "position": "55092604",
            "identifier": "EGFR",
            "inclusion": True,
            "armSpecific": False
        }
    ],
    "geneFusions": [],
    "unifiedGeneFusions": [],
    "nonHotspotRules": [],
}

if 'TOKEN_ID' in os.environ:
    headers = {"Authorization": "Bearer {}".format(os.environ['TOKEN_ID'])}
    resp = requests.patch('http://localhost:5010/api/v1/treatment_arms/amois', json=vr, headers=headers)
    pprint.pprint(resp.json())
    print("")

    is_amoi_json = {"type": "singleNucleotideVariants", "variants": vr['singleNucleotideVariants']}
    resp = requests.patch('http://localhost:5010/api/v1/treatment_arms/is_amoi', json=is_amoi_json, headers=headers)
    pprint.pprint(resp.json())
    print("")


else:
    print("TOKEN_ID environment variable not found.")
