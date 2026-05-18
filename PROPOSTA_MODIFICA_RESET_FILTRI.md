# Proposta Modifica: Reset filtri `st.pills` non completo

## Problema riscontrato
Nel file `main.py`, cliccando su **"🔄 RESET FILTRI"** alcuni filtri risultano ancora preselezionati.

## Causa probabile
La funzione `perform_reset()` rimuove solo le chiavi di sessione che iniziano con `pill_`:

```python
if key.startswith("pill_"):
    del st.session_state[key]
```

In alcuni casi Streamlit può usare chiavi interne/namespaced legate ai widget, quindi il controllo solo con `startswith("pill_")` non intercetta tutte le chiavi collegate ai `pills`.

## Modifica proposta
Aggiornare il reset per cancellare tutte le chiavi correlate ai filtri `pills`:

```python
def perform_reset():
    # Svuota tutti i widget selezionati (anche eventuali chiavi namespaced)
    keys_to_clear = [k for k in list(st.session_state.keys()) if k.startswith("pill_") or "pill_" in k]
    for key in keys_to_clear:
        del st.session_state[key]

    # Incrementa il contatore per forzare la rigenerazione dei widget
    st.session_state.reset_counter += 1
    st.rerun()
```

## Beneficio
Il pulsante di reset torna a comportamento coerente: i filtri vengono effettivamente azzerati e l'interfaccia non mostra selezioni residue.

## Verifica suggerita
1. Avviare l'app Streamlit.
2. Selezionare più filtri in sezioni diverse.
3. Cliccare su **"🔄 RESET FILTRI"**.
4. Verificare che nessun `pill` rimanga selezionato e che la lista board torni allo stato iniziale.
