import pandas as pd

#Runs a SPARQL query and stores the result as a pandas DataFrame. Also shortens URI columns if wanted
def query_to_dataframe(graph, query, shorten_columns=None):
    results = graph.query(query)

    rows = []
    for row in results:
        row_dict = {}

        for var, value in zip(results.vars, row):
            var_name = str(var)

            if value is None:
                row_dict[var_name] = None
            elif shorten_columns and var_name in shorten_columns:
                row_dict[var_name] = shorten_uri(value)
            else:
                row_dict[var_name] = value.toPython()

        rows.append(row_dict)

    return pd.DataFrame(rows)

def shorten_uri(uri):
    return str(uri).split("/")[-1].replace("_", " ")