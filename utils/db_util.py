#!/usr/bin/python
import logging
import sys
from bottle import abort
from elasticsearch import Elasticsearch, helpers

class DBUtil(object):
    """This class provides helper methods to be used in Efetch and its plugins"""
    elasticsearch = None

    def __init__(self, es_url=None):
        """Creates the Efetch indices in Eleasticsearch if they do not exist"""
        if es_url:
            self.elasticsearch = Elasticsearch([es_url])
        else:
            self.elasticsearch = Elasticsearch()
   
        #Elastic Search Setup
        self.elasticsearch.indices.create(index='efetch-config',ignore=400)
        self.elasticsearch.indices.create(index='efetch-log',ignore=400)
        self.elasticsearch.indices.create(index='efetch-cases',ignore=400)
        self.elasticsearch.indices.create(index='efetch-evidence',ignore=400)
        self.elasticsearch.indices.put_template(name="efetch-case", body=case_template())
        self.elasticsearch.indices.put_template(name="efetch-evidence", body=evidence_template())

    def get_file_from_ppid(self, ppid, abort_on_error=True):
        """Returns the file object for the given file in the database"""
        return self.get_file(ppid.split('/')[0], ppid, abort_on_error)
   
    def query(self, query, image_id):
        """Returns the results of an Elastic Search query without error checking"""
        return self.elasticsearch.search(index='efetch-evidence_' + image_id, body=query)

    def bool_query(self, directory, bool_query = {}, size=10000, use_directory=True):
        """Returns the results of an Elastic Search boolean query within a given directory"""
        #REF: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
        #TODO: Loop through if size > 10000
        if 'readyState' in bool_query:
            del bool_query['readyState']
        bool_query = self.append_dict(bool_query, 'must', { 'term': { 'dir': directory['pid'] + '/' } })
        query = { 'query': { 'bool': bool_query, }, 'size': size} 
        return self.elasticsearch.search(index='efetch-evidence_' + directory['image_id'], body=query)

    def bool_query_evidence(self, directory, bool_query = {}, size=10000):
        """Returns a list of evidence for an Elastic Search boolean query within a directory"""
        result = self.bool_query(directory, bool_query, size)
        return [(evidence['_source']) for evidence in result['hits']['hits']]

    def append_dict(self, dictionary, key, value):
        """Appends values to a dictionary in the format Elasticsearch expects"""
        if not dictionary:
            dictionary = {}
        if not key in dictionary:
            dictionary[key] = value
        elif isinstance(dictionary[key], list):
            list(dictionary[key]).append(value)
        else:
            dictionary[key] = [ dictionary[key], value]
        
        return dictionary

    def create_case(self, name, description, evidence):
        """Creates a case in Elastic Search under the efetch-cases index"""
        if not name:
            return
        case = {
                    '_index': 'efetch-cases',
                    '_type' : 'case',
                    '_id' : name,
                    '_source' : {
                        'name' : name,
                        'description' : description,
                        'evidence' : evidence
                    }
            }
        json = []
        json.append(case)
        helpers.bulk(self.elasticsearch, json)
        return

    def update_case(self, name, new_name, description, evidence):
        """Updates the current case"""
        #TODO switch to actual update
        self.delete_case(name)
        return self.create_case(new_name, description, evidence)

    def add_evidence_to_case(self, name, evidence, abort_on_error=True):
        """Adds a list of evidence to a given case by using the update_case method"""
        case = self.read_case(name)
        curr_evidence = case['_source']['evidence']
        description = case['_source']['description']
        return self.update_case(name, name, description, curr_evidence + evidence)

    def remove_evidence_from_case(self, name, evidence, abort_on_error=True):
        """Removes a list of evidence from a given case by using the update_case method"""
        case = self.read_case(name)
        curr_evidence = case['_source']['evidence']
        description = case['_source']['description']
        return self.update_case(name, name, description, [e for e in curr_evidence if e not in evidence])

    def get_evidence(self, name=None, abort_on_error=True):
        """Gets Efetch root evidence by name from Elastic Search"""
        if not name:
            indices = self.elasticsearch.indices.get_aliases().keys()
            evidence = []
            for index in sorted(indices):
                if str(index).startswith('efetch-evidence_'):
                    evidence.append(index[16:])
            return evidence
        else:
            return self.read_case(name)['_source']['evidence']

    def read_case(self, name=None, abort_on_error=True):
        """Gets Efetch case by name from Elastic Search"""
        if not name:
            return self.elasticsearch.search(index='efetch-cases', doc_type='case')
        return self.elasticsearch.get(index='efetch-cases', doc_type='case', id=name)

    def delete_case(self, name):
        """Deletes Efetch case by name from Elastic Search"""
        self.elasticsearch.delete(index='efetch-cases', doc_type='case', id=name)
        return

    def get_file(self, image_id, evd_id, abort_on_error=True):
        """Returns the file object for the given file in the database"""
        
        #Remove leading and trailing slashes
        if evd_id.endswith('/'):
            evd_id = evd_id[:-1]
        if str(evd_id).startswith('/'):
            evd_id = str(evd_id)[1:]

        #TODO CHECK IF IMAGE EXISTS
        #TODO Do not hide errors from elasticsearch
        curr_file = self.elasticsearch.search(index='efetch-evidence_' + image_id, doc_type='event', body={"query": {"match": {"pid": evd_id}}})
        if not curr_file['hits'] or not curr_file['hits']['hits'] or not curr_file['hits']['hits'][0]['_source']:
            logging.error("Could not find file. Image='" + image_id + "' Type='" + input_type + "' _id='" + evd_id + "'")
            if abort_on_error:
                abort(404, "Could not find file in provided image.")
            else:
                return
    
        if len(curr_file['hits']['hits']) > 1:
            logging.warn("Found more than one file with pid " + evd_id)

        return curr_file['hits']['hits'][0]['_source']

    def create_index(self, index_name):
        """Create index in Elastic Search with the provided name"""
        self.elasticsearch.indices.create(index=index_name, ignore=400)

    def bulk(self, json):
        """Bulk adds json to Elastic Search"""
        helpers.bulk(self.elasticsearch, json)

    def update_by_ppid(self, ppid, update, abort_on_error=True):
        """Returns the file object for the given file in the database"""
        ppid_split = str(ppid).split('/')
        image_id = ppid_split[0]
        path = '/'.join(ppid_split[1:])
        self.update(ppid, image_id, update, abort_on_error)

    def update(self, ppid, image_id, update, abort_on_error=True):
        """Updates evidence event in Elastic Search"""
        self.elasticsearch.update(index='efetch-evidence_' + image_id, doc_type='event', id=ppid, body={'doc': update})
    
def evidence_template():
    """Returns the Elastic Search mapping for Evidence"""
    return {
        "template" : "efetch-evidence*",
        "settings" : {
            "number_of_shards" : 1
            },
        "mappings" : {
            "_default_" : {
                "_source" : { "enabled" : True },
                "properties" : {
                    "root" : {"type": "string", "index" : "not_analyzed"},
                    "pid" : {"type": "string", "index" : "not_analyzed"},
                    "iid" : {"type": "string", "index" : "not_analyzed"},
                    "image_id": {"type": "string", "index" : "not_analyzed"},
                    "image_path" : {"type": "string", "index" : "not_analyzed"},
                    "evd_type" : {"type": "string", "index" : "not_analyzed"},
                    "name" : {"type": "string", "index" : "not_analyzed"},
                    "path" : {"type": "string", "index" : "not_analyzed"},
                    "ext" : {"type": "string", "index" : "not_analyzed"},
                    "dir" : {"type": "string", "index" : "not_analyzed"},
                    "meta_type" : {"type": "string", "index" : "not_analyzed"},
                    "inode" : {"type": "string", "index" : "not_analyzed"},
                    "mtime" : {"type": "string", "index" : "not_analyzed"},
                    "atime" : {"type": "string", "index" : "not_analyzed"},
                    "ctime" : {"type": "string", "index" : "not_analyzed"},
                    "crtime" : {"type": "string","index" : "not_analyzed"},
                    "file_size" : {"type": "string", "index" : "not_analyzed"},
                    "uid" : {"type": "string", "index" : "not_analyzed"},
                    "gid" : {"type": "string", "index" : "not_analyzed"},
                    "driver" : {"type": "string", "index" : "not_analyzed"},
                    "source_short" : {"type": "string", "index" : "not_analyzed"}
                    }
            }
        }
    }

def case_template():
    """Returns the Elastic Search mapping for Efetch Cases"""
    return {
        "template" : "efetch-cases",
        "settings" : {
            "number_of_shards" : 1
            },
        "mapping" : {
            "_default_" : {
                "_source" : { "enabled" : True },
                "properties" : {
                    "name" : {"type": "string", "index" : "not_analyzed"},
                    "description" : {"type": "string", "index" : "analyzed"},
                    "evidence" : {
                        "properties" : {
                                "evidence" : {"type" : "string", "index" : "not_analyzed" }
                            }
                        }
                    }
                }
            }
        }

