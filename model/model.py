import copy
import networkx as nx
from database.DAO import DAO

class Model:
    def __init__(self):
        self.mappa_nodi = {}
        self.grafo = nx.Graph()

    def getAllLocalizations(self):
        return DAO.get_all_localizations()

    def popola_nodi(self, localization):
        # La chiami all'avvio o prima di fare il grafo
        self.mappa_nodi.clear()
        lista_nodi = DAO.get_all_nodi(localization)
        for nodo in lista_nodi:
            self.mappa_nodi[nodo.GeneID] = nodo




    def build_graph(self, localization):
        self.grafo.clear()
        self.popola_nodi(localization)

        # PASSO 2: Aggiunta Nodi (Scegli opzione Standard o Union dal DAO)
        self.grafo.add_nodes_from(self.mappa_nodi.values())

        # PASSO 3: Archi (Scegli Semplici o Ninja/Pesati dal DAO)
        archi_grezzi = DAO.get_all_archi()

        for arco in archi_grezzi:
            if arco.GeneID1 == arco.GeneID2:
                continue
            if arco.GeneID1 in self.mappa_nodi and arco.GeneID2 in self.mappa_nodi:
                n1 = self.mappa_nodi[arco.GeneID1]
                n2 = self.mappa_nodi[arco.GeneID2]


                peso_arco = 0
                for peso in DAO.get_pesi_arco(arco.GeneID1, arco.GeneID2):
                    peso_arco += peso

                self.grafo.add_edge(n1, n2, weight=peso_arco)

    def get_dettagli_grafo(self):
        return self.grafo.number_of_nodes(), self.grafo.number_of_edges()

    def get_top_archi_peso(self, n):
        # 1. Estraggo tutti gli archi e li trasformo in lista
        lista_archi = list(self.grafo.edges(data=True))

        # 2. Li ordino in base al valore 'weight' dentro il dizionario 'data', al contrario (decrescente)
        lista_archi.sort(key=lambda edge: edge[2]['weight'])

        # 3. Restituisco i primi N elementi
        return lista_archi[:n]

    def get_componenti_connesse(self):
        result=[]

        # 2. Ottengo una lista di "set" (insiemi) contenenti i nodi di ciascuna componente connessa
        componenti = list(nx.connected_components(self.grafo))

        # 3. Trovo quella più grande usando len() come chiave per la ricerca del massimo
        if not componenti:
            return 0, []
        for componente in componenti:
            c = list(componente)
            if len(c)>1:
                result.append(c)

        return sorted(result, key=len, reverse=True)

    def calcola_sottoinsieme_ottimo(self):
        # 1. Inizializzo i record da battere
        self._max_len = 0
        self._min_comp = float('inf')  # Infinito, perché cerchiamo il minimo!
        self._miglior_set = []

        # 2. Filtro i nodi scartando i "?" e li divido (Punto II)
        # 🚨 ATTENZIONE: Sostituisci '.Essential' con il nome esatto dell'attributo nel tuo DTO!
        nodi_essenziali = [n for n in self.grafo.nodes() if n.Essential == "Essential"]
        nodi_non_essenziali = [n for n in self.grafo.nodes() if n.Essential == "Non-Essential"]

        # 3. Li ordino per GeneID PRIMA della ricorsione (Punto I).
        # In questo modo ogni sottoinsieme creato sarà già ordinato.
        # 🚨 ATTENZIONE: Sostituisci '.GeneID' con il nome reale dell'attributo!
        nodi_essenziali.sort(key=lambda x: x.GeneID)
        nodi_non_essenziali.sort(key=lambda x: x.GeneID)

        # 4. Lancio la ricorsione sui due "mondi" separati
        self._ricorsione_subset([], nodi_essenziali, 0)
        self._ricorsione_subset([], nodi_non_essenziali, 0)

        return self._miglior_set, self._max_len, self._min_comp

    def _ricorsione_subset(self, parziale, nodi_validi, pos):
        # 1. VALUTAZIONE DELLA SOLUZIONE
        if len(parziale) > 0:
            # Estraggo il sottografo e conto le isole (Punto IV)
            sottografo = self.grafo.subgraph(parziale)
            comp_connesse = nx.number_connected_components(sottografo)

            # Controllo 1: Ho battuto il record di lunghezza? (Punto III)
            if len(parziale) > self._max_len:
                self._max_len = len(parziale)
                self._min_comp = comp_connesse
                self._miglior_set = copy.deepcopy(parziale)

            # Controllo 2: A parità di lunghezza, ho meno componenti connesse? (Punto IV)
            elif len(parziale) == self._max_len:
                if comp_connesse < self._min_comp:
                    self._min_comp = comp_connesse
                    self._miglior_set = copy.deepcopy(parziale)

        # 2. PRUNING (Salvavita per l'esame)
        # Se i nodi che ho in mano + quelli che mancano da esplorare sono MENO
        # del record attuale, è impossibile battere il record. Mi fermo subito!
        nodi_rimanenti = len(nodi_validi) - pos
        if len(parziale) + nodi_rimanenti < self._max_len:
            return

        # 3. ESPLORAZIONE
        for i in range(pos, len(nodi_validi)):
            nodo = nodi_validi[i]

            parziale.append(nodo)

            # Vado in profondità spostando la 'pos' a i+1 per non ripescare lo stesso nodo
            self._ricorsione_subset(parziale, nodi_validi, i + 1)

            # Backtracking
            parziale.pop()







