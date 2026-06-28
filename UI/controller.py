import flet as ft
from UI.view import View
from model.model import Model


class Controller:

    def __init__(self, view: View, model: Model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def populate_dd_localizations(self):
        self._view.dd_localization.options.clear()
        dati = self._model.getAllLocalizations()
        for dato in dati:
            self._view.dd_localization.options.append(ft.dropdown.Option(str(dato)))
        pass

    def handle_graph(self, e):
        # 1. LETTURA INPUT E CONTROLLO ERRORI
        valore_str = self._view.dd_localization.value

        if valore_str is None:
            self._view.create_alert("Attenzione: seleziona un valore dalla tendina")
            return

        try:
            parametro_utente = str(valore_str)
        except ValueError:
            self._view.create_alert("Attenzione: seleziona un valore valido dalla tendina")
            return


        # 2. CHIAMATA AL MODEL
        self._model.build_graph(parametro_utente)

        # 3. PULIZIA SCHERMO E VERIFICA
        self._view.txt_result.controls.clear()

        if self._model.grafo.number_of_nodes() == 0:
            self._view.txt_result.controls.append(ft.Text("Nessun grafo creato con questi parametri."))
            self._view.update_page()
            return

        # 4. STAMPA DELLE RISPOSTE STANDARD
        nodi, archi = self._model.get_dettagli_grafo()
        self._view.txt_result.controls.append(ft.Text(f"Grafo creato con successo!", color="green"))
        self._view.txt_result.controls.append(ft.Text(f"Numero Nodi: {nodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero Archi: {archi}"))

        # ---> TRUCCO: STAMPA ARCHI E PESI (Scommenta se richiesto)
        # for u, v, data in self._model.grafo.edges(data=True):
        #     peso = data.get('weight', 'N/A')
        #     self._view.txt_result.controls.append(ft.Text(f"{u.nome} <---> {v.nome} | Peso: {peso}"))

        # a) Stampa i tre archi di peso maggiore
        self._view.txt_result.controls.append(ft.Text("Archi:", color="red"))
        top_archi = self._model.get_top_archi_peso(archi)
        for u, v, dati in top_archi:
            self._view.txt_result.controls.append(ft.Text(f"{u.GeneID} <-> {v.GeneID} peso:{dati['weight']}"))
        self._view.update_page()

    def analyze_graph(self, e):

        self._view.txt_result.controls.append(ft.Text(f"Componenti connesse", color="red"))
        componenti = self._model.get_componenti_connesse()

        if componenti is not None:
            for componente in componenti:
                for nodo in componente:
                    self._view.txt_result.controls.append(ft.Text(f"{nodo.GeneID}, "))

                self._view.txt_result.controls.append(ft.Text(f"dimensione componente: {len(componente)}"))

        self._view.update_page()

    def handle_ricerca_avanzata(self, e):
        # Pulisco lo schermo dai vecchi risultati
        self._view.txt_result.controls.clear()

        # Chiamo il Model senza passare parametri, fa tutto da solo!
        miglior_set, max_len, min_comp = self._model.calcola_sottoinsieme_ottimo()

        # Controllo di sicurezza
        if not miglior_set:
            self._view.txt_result.controls.append(ft.Text("Nessun set valido trovato.", color="red"))
            self._view.update_page()
            return

        # Stampa dei risultati
        self._view.txt_result.controls.append(
            ft.Text(f"Sottoinsieme ottimo trovato!", color="blue", weight="bold")
        )
        self._view.txt_result.controls.append(
            ft.Text(f"Lunghezza (numero nodi): {max_len}")
        )
        self._view.txt_result.controls.append(
            ft.Text(f"Componenti connesse del sottografo: {min_comp}")
        )

        self._view.txt_result.controls.append(
            ft.Text("\nSequenza cromosomi (ordinata per GeneID):", color="green", weight="bold")
        )

        # Stampa di verifica
        for nodo in miglior_set:
            # 🚨 ATTENZIONE: Usa il nome reale dei campi del tuo oggetto!
            self._view.txt_result.controls.append(
                ft.Text(f"- {nodo.GeneID} (GeneID: {nodo.GeneID} | {nodo.Essential})")
            )

        self._view.update_page()

