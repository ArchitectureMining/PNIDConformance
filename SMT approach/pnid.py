from xml.dom import minidom
from html import unescape

class PNID:
    def __init__(self, pnid_as_array):
        self.net = pnid_as_array
        self._places = pnid_as_array["places"]
        self._transitions = pnid_as_array["transitions"]
        self._arcs = pnid_as_array["arcs"]

    def places(self):
        return self._places

    def transitions(self):
        return self._transitions

    def arcs(self):
        return self._arcs

    def get_input_arcs(self, id):
        arcs = []
        for arc in self["arcs"]:
            if arc["tgt"] == id:
                arcs.append(arc)
        return arcs

    def get_output_arcs(self, id):
        arcs = []
        for arc in self["arcs"]:
            if arc["src"] == id:
                arcs.append(arc)
        return arcs

    def read_pnml_input(pnmlfile):
        dom = minidom.parse(pnmlfile)

        pnid = {"variables": [], "places": [], "transitions": [], "arcs": []}

        # Arcs
        for a in dom.getElementsByTagName("arc"):
            src = a.getAttribute("source")
            tgt = a.getAttribute("target")
            id = a.getAttribute("id")
            if a.getElementsByTagName("inscription"):
                inscription_elem = a.getElementsByTagName("inscription")[0]
                inscription = "";
                index= 0;
                for node in inscription_elem.getElementsByTagName("text"):
                    if index == 0:
                        inscription = inscription + node.firstChild.nodeValue
                    else:
                        inscription = inscription + "," + node.firstChild.nodeValue
                    index = index + 1;
            else:
                inscription = ""
            arc = {
                "src": src,
                "tgt": tgt,
                "id": id,
                "inscription": unescape(inscription),
            }
            pnid["arcs"].append(arc)

        # Transitions
        for a in dom.getElementsByTagName("transition"):
            id = a.getAttribute("id")
            inArcs = PNID.get_input_arcs(pnid, id)
            outArcs = PNID.get_output_arcs(pnid, id)
            t = {"id": id, "inArcs": inArcs, "outArcs": outArcs}
            pnid["transitions"].append(t)

        # Places
        for a in dom.getElementsByTagName("page")[0].getElementsByTagName("place"):
            id = a.getAttribute("id")
            p = {"id": id, "vector_size": 0}
            init = a.getElementsByTagName("initialMarking")
            if len(init) > 0:
                p["initial"] = 1
                for arc in pnid["arcs"]:
                    if arc["src"] == id and len(arc["inscription"]) > 0:
                        p["vector_size"] = len(arc["inscription"].split(","))
            pnid["places"].append(p)

        return PNID(pnid)
