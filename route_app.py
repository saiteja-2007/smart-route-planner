#!/usr/bin/env python3
"""
KERALA SMART ROUTE PLANNER

"""


import csv
import difflib
import os

import networkx as nx

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data") if os.path.isdir(os.path.join(BASE, "data")) else BASE

LINE = "-" * 62


def load():
    G = nx.Graph()
    place_district = {}
    with open(os.path.join(DATA, "kerala_places.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            place_district[row["name"]] = row["district"]
    with open(os.path.join(DATA, "kerala_roads.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            G.add_edge(row["from_place"], row["to_place"],
                       distance_km=float(row["distance_km"]),
                       travel_time_min=float(row["travel_time_min"]))
    return G, place_district


def show_all(place_district):
    by_district = {}
    for name, d in place_district.items():
        by_district.setdefault(d, []).append(name)
    print("\n  All available places:")
    for d in sorted(by_district):
        print(f"   {d}: " + ", ".join(sorted(by_district[d])))
    print()


def ask_place(prompt, names, place_district):
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "list":
            show_all(place_district)
            continue
        if not raw:
            continue
        for n in names:                      # exact match, case-insensitive
            if n.lower() == raw.lower():
                return n
        close = difflib.get_close_matches(   # typo -> suggest closest
            raw.lower(), [n.lower() for n in names], n=1, cutoff=0.6)
        if close:
            for n in names:
                if n.lower() == close[0]:
                    print(f"   '{raw}' not found. Did you mean '{n}'? Try again.")
                    break
        else:
            print(f"   '{raw}' not found. Type 'list' to see all places.")


def main():
    G, place_district = load()
    names = sorted(place_district)

    print("=" * 62)
    print("      KERALA SMART ROUTE PLANNER   (NetworkX + Dijkstra)")
    print("=" * 62)
    print(f" Loaded {G.number_of_nodes()} places, {G.number_of_edges()} roads "
          f"(shortest route by distance).")
    print(" Type 'list' to see all places.\n")

    while True:
        src = ask_place(" Starting place : ", names, place_district)
        dst = src
        while dst == src:
            dst = ask_place(" Destination    : ", names, place_district)
            if dst == src:
                print("   Start and destination are the same - pick another.")

        path = nx.dijkstra_path(G, src, dst, weight="distance_km")
        km = nx.dijkstra_path_length(G, src, dst, weight="distance_km")
        mins = sum(G[a][b]["travel_time_min"] for a, b in zip(path, path[1:]))

        print("\n" + LINE)
        print(f" ROUTE: {src}  ->  {dst}")
        print(LINE)
        for i, p in enumerate(path, 1):
            leg = "" if i == 1 else f"  +{G[path[i - 2]][p]['distance_km']:.1f} km"
            print(f"  {i:>2}. {p:<24}{leg}")
        print(LINE)
        mids = path[1:-1]
        print(f" Distance : {km:.0f} km        Time : ~{mins / 60:.1f} h")
        print(f" Cities in between ({len(mids)}): "
              + (", ".join(mids) if mids else "none - direct road"))
        print(LINE)

        if input("\n Another route? (y/n): ").strip().lower() not in ("y", "yes"):
            print(" Bye!")
            break


if __name__ == "__main__":
    main()
