import numpy as np
from sklearn.metrics.pairwise import pairwise_distances

from meeshkan.nlp.schema_normalizer.schema_relations.feature_extraction import FeatureExtraction


def get_all_paths(specs_dict):
    if specs_dict.get('paths') is None:
        raise KeyError("The key 'paths' is not present in specs  ")

    return [path for path in specs_dict['paths'].keys()]

def get_all_properties(specs_dict):
    all_paths = get_all_paths(specs_dict)
    if len(all_paths) > 1:
        all_paths_dict = {key: [] for key in all_paths}
        methods = ['get', 'post']
        for path in all_paths:
            for method in specs_dict['paths'][path].keys():
                if method in methods:
                    schema = specs['paths'][path][method]['responses']['200']['content']['application/json']['schema']
                    schema['$schema'] = 'root'
                    schema_feats = generate_schema_vectors(schema)
                    parsed_feats = parse_schema_features(schema_feats)
                    all_paths_dict[path].append({method: parsed_feats})
                    break  # To ensure that only single method is picked for any endpoint

        return all_paths, all_paths_dict
    return all_paths, None


def calc_distance(spes_dict):
    all_paths, all_paths_dict = get_all_properties(spes_dict)
    all_distances = list()
    methods = ['get', 'post']
    if all_paths_dict is None:
        return []
    else:
        embedding_dict = {key : [] for key in all_paths}
        fe = FeatureExtraction()
        for keys, values in all_paths_dict.items():
            for method in values[0].keys():
                embedding_dict[keys] = fe.generate_nlp_vector(values[0][method])
        embedding_list = list()
        for path in all_paths:
            embedding_list.append(embedding_dict[path])

        embedding_list = np.array(embedding_list)
        distance_matrix = pairwise_distances(embedding_list, metric='cosine')

        api_nearest_dict = dict()
        paths_nearest_value = list()
        for index, path in enumerate(all_paths):
            nearest_index = distance_matrix[index,].argsort()[1]
            paths_nearest_value.append(distances[index, nearest_index])
            api_nearest_dict[path] = all_paths[nearest_index]

        threshold = 0.1
        paths_unique_dict = dict()
        for index, path in enumerate(all_paths):
            if paths_nearest_value[index] < threshold:
                if path != paths_unique_dict.get(api_nearest_dict[path]):
                    paths_unique_dict[path] = api_nearest_dict[path]

        paths_tuple_list = list()
        for key, value in paths_unique_dict.items():
            paths_tuple_list.append((key, value))

        return paths_tuple_list





        


