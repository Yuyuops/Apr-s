#!/usr/bin/env python3
"""Builds the Pisa and Vesuvius test modules (32x32 windows of the Italia grid). usage: module_pisa_vesuvio.py OUTROOT"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import region
root = sys.argv[1]
S, m, F = region.build_region(os.path.join(root, "pisa_v2"), 24, 32, 32, 32, [dict(type="pisa", row=38, col=42, footprint=[6, 6], lean=1)], title="Pisa v2"); print("pisa", m["pieces"], m["modules"])
S, m, F = region.build_region(os.path.join(root, "vesuvio_v3"), 52, 60, 32, 32, [dict(type="vesuvio", row=63, col=70, footprint=[12, 12])], title="Vesuvio v3"); print("vesuvio", m["pieces"], m["modules"])
