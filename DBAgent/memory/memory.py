import requests
import os
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Iterable, Type, Union, Callable, Optional, Any
from huggingface_hub import HfApi, HfFolder, Repository, hf_hub_url, cached_download
import fnmatch
import numpy as np
import importlib
from memory.Pooling import Pooling
from memory.Transformer import Transformer
from numpy import ndarray
import pandas as pd
from collections import OrderedDict
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE
import torch
import json
from pydantic import BaseModel, Extra, Field
import re
import logging
from torch import nn, Tensor, device
from tqdm.autonotebook import trange
from pathlib import Path
load_dotenv()

DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
logger = logging.getLogger(__name__)
__MODEL_HUB_ORGANIZATION__ = 'sentence-transformers'
__version__ = "2.2.2"
class MemoryManager:
    def __init__(self, gpt):
        self.gpt = gpt
    def store_memory(self, message, result, action, summary):
        system_prompt = """I am an autonomous database agent.
        I need to store my thoughts into long term memory.
        My summary on the action I just performed is:
        {summary}"""
        prompt = """My original message is: {message}
        My action is: {result}
        The result of my action is: {action}
        """
        response = self.gpt.chat_with_gpt3(system_prompt, prompt.format(message=message, result=result, action=action, summary=summary))
        print(response)
        return response

class SentenceTransformer(nn.Sequential):
    """
    Loads or create a SentenceTransformer model, that can be used to map sentences / text to embeddings.

    :param model_name_or_path: If it is a filepath on disc, it loads the model from that path. If it is not a path, it first tries to download a pre-trained SentenceTransformer model. If that fails, tries to construct a model from Huggingface models repository with that name.
    :param modules: This parameter can be used to create custom SentenceTransformer models from scratch.
    :param device: Device (like 'cuda' / 'cpu') that should be used for computation. If None, checks if a GPU can be used.
    :param cache_folder: Path to store models. Can be also set by SENTENCE_TRANSFORMERS_HOME enviroment variable.
    :param use_auth_token: HuggingFace authentication token to download private models.
    """
    def __init__(self, model_name_or_path: Optional[str] = None,
                 modules: Optional[Iterable[nn.Module]] = None,
                 device: Optional[str] = None,
                 cache_folder: Optional[str] = None,
                 use_auth_token: Union[bool, str, None] = None
                 ):
        self._model_card_vars = {}
        self._model_card_text = None
        self._model_config = {}

        if cache_folder is None:
            cache_folder = os.getenv('SENTENCE_TRANSFORMERS_HOME')
            if cache_folder is None:
                try:
                    from torch.hub import _get_torch_home

                    torch_cache_home = _get_torch_home()
                except ImportError:
                    torch_cache_home = os.path.expanduser(os.getenv('TORCH_HOME', os.path.join(os.getenv('XDG_CACHE_HOME', '~/.cache'), 'torch')))

                cache_folder = os.path.join(torch_cache_home, 'sentence_transformers')

        if model_name_or_path is not None and model_name_or_path != "":
            logger.info("Load pretrained SentenceTransformer: {}".format(model_name_or_path))

            #Old models that don't belong to any organization
            basic_transformer_models = ['albert-base-v1', 'albert-base-v2', 'albert-large-v1', 'albert-large-v2', 'albert-xlarge-v1', 'albert-xlarge-v2', 'albert-xxlarge-v1', 'albert-xxlarge-v2', 'bert-base-cased-finetuned-mrpc', 'bert-base-cased', 'bert-base-chinese', 'bert-base-german-cased', 'bert-base-german-dbmdz-cased', 'bert-base-german-dbmdz-uncased', 'bert-base-multilingual-cased', 'bert-base-multilingual-uncased', 'bert-base-uncased', 'bert-large-cased-whole-word-masking-finetuned-squad', 'bert-large-cased-whole-word-masking', 'bert-large-cased', 'bert-large-uncased-whole-word-masking-finetuned-squad', 'bert-large-uncased-whole-word-masking', 'bert-large-uncased', 'camembert-base', 'ctrl', 'distilbert-base-cased-distilled-squad', 'distilbert-base-cased', 'distilbert-base-german-cased', 'distilbert-base-multilingual-cased', 'distilbert-base-uncased-distilled-squad', 'distilbert-base-uncased-finetuned-sst-2-english', 'distilbert-base-uncased', 'distilgpt2', 'distilroberta-base', 'gpt2-large', 'gpt2-medium', 'gpt2-xl', 'gpt2', 'openai-gpt', 'roberta-base-openai-detector', 'roberta-base', 'roberta-large-mnli', 'roberta-large-openai-detector', 'roberta-large', 't5-11b', 't5-3b', 't5-base', 't5-large', 't5-small', 'transfo-xl-wt103', 'xlm-clm-ende-1024', 'xlm-clm-enfr-1024', 'xlm-mlm-100-1280', 'xlm-mlm-17-1280', 'xlm-mlm-en-2048', 'xlm-mlm-ende-1024', 'xlm-mlm-enfr-1024', 'xlm-mlm-enro-1024', 'xlm-mlm-tlm-xnli15-1024', 'xlm-mlm-xnli15-1024', 'xlm-roberta-base', 'xlm-roberta-large-finetuned-conll02-dutch', 'xlm-roberta-large-finetuned-conll02-spanish', 'xlm-roberta-large-finetuned-conll03-english', 'xlm-roberta-large-finetuned-conll03-german', 'xlm-roberta-large', 'xlnet-base-cased', 'xlnet-large-cased']

            if os.path.exists(model_name_or_path):
                #Load from path
                model_path = model_name_or_path
            else:
                #Not a path, load from hub
                if '\\' in model_name_or_path or model_name_or_path.count('/') > 1:
                    raise ValueError("Path {} not found".format(model_name_or_path))

                if '/' not in model_name_or_path and model_name_or_path.lower() not in basic_transformer_models:
                    # A model from sentence-transformers
                    model_name_or_path = __MODEL_HUB_ORGANIZATION__ + "/" + model_name_or_path

                model_path = os.path.join(cache_folder, model_name_or_path.replace("/", "_"))
                
                if not os.path.exists(os.path.join(model_path, 'modules.json')):
                    # Download from hub with caching
                    self.snapshot_download(model_name_or_path,
                                        cache_dir=cache_folder,
                                        library_name='sentence-transformers',
                                        library_version=__version__,
                                        ignore_files=['flax_model.msgpack', 'rust_model.ot', 'tf_model.h5'],
                                        use_auth_token=use_auth_token)

            if os.path.exists(os.path.join(model_path, 'modules.json')):    #Load as SentenceTransformer model
                modules = self._load_sbert_model(model_path)
            else:   #Load with AutoModel
                modules = self._load_auto_model(model_path)

        if modules is not None and not isinstance(modules, OrderedDict):
            modules = OrderedDict([(str(idx), module) for idx, module in enumerate(modules)])

        super().__init__(modules)
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Use pytorch device: {}".format(device))

        self._target_device = torch.device(device)


    
    def encode(self, sentences: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = None,
        output_value: str = 'sentence_embedding',
        convert_to_numpy: bool = True,
        convert_to_tensor: bool = False,
        device: str = None,
        normalize_embeddings: bool = False) -> Union[List[Tensor], ndarray, Tensor]:
        """
        Computes sentence embeddings

        :param sentences: the sentences to embed
        :param batch_size: the batch size used for the computation
        :param show_progress_bar: Output a progress bar when encode sentences
        :param output_value:  Default sentence_embedding, to get sentence embeddings. Can be set to token_embeddings to get wordpiece token embeddings. Set to None, to get all output values
        :param convert_to_numpy: If true, the output is a list of numpy vectors. Else, it is a list of pytorch tensors.
        :param convert_to_tensor: If true, you get one large tensor as return. Overwrites any setting from convert_to_numpy
        :param device: Which torch.device to use for the computation
        :param normalize_embeddings: If set to true, returned vectors will have length 1. In that case, the faster dot-product (util.dot_score) instead of cosine similarity can be used.

        :return:
            By default, a list of tensors is returned. If convert_to_tensor, a stacked tensor is returned. If convert_to_numpy, a numpy matrix is returned.
        """
        self.eval()
        if show_progress_bar is None:
            show_progress_bar = (logger.getEffectiveLevel()==logging.INFO or logger.getEffectiveLevel()==logging.DEBUG)

        if convert_to_tensor:
            convert_to_numpy = False

        if output_value != 'sentence_embedding':
            convert_to_tensor = False
            convert_to_numpy = False

        input_was_string = False
        if isinstance(sentences, str) or not hasattr(sentences, '__len__'): #Cast an individual sentence to a list with length 1
            sentences = [sentences]
            input_was_string = True

        if device is None:
            device = self._target_device

        self.to(device)

        all_embeddings = []
        length_sorted_idx = np.argsort([-self._text_length(sen) for sen in sentences])
        sentences_sorted = [sentences[idx] for idx in length_sorted_idx]

        for start_index in trange(0, len(sentences), batch_size, desc="Batches", disable=not show_progress_bar):
            sentences_batch = sentences_sorted[start_index:start_index+batch_size]
            features = self.tokenize(sentences_batch)
            features = self.batch_to_device(features, device)

            with torch.no_grad():
                out_features = self.forward(features)

                if output_value == 'token_embeddings':
                    embeddings = []
                    for token_emb, attention in zip(out_features[output_value], out_features['attention_mask']):
                        last_mask_id = len(attention)-1
                        while last_mask_id > 0 and attention[last_mask_id].item() == 0:
                            last_mask_id -= 1

                        embeddings.append(token_emb[0:last_mask_id+1])
                elif output_value is None:  #Return all outputs
                    embeddings = []
                    for sent_idx in range(len(out_features['sentence_embedding'])):
                        row =  {name: out_features[name][sent_idx] for name in out_features}
                        embeddings.append(row)
                else:   #Sentence embeddings
                    embeddings = out_features[output_value]
                    embeddings = embeddings.detach()
                    if normalize_embeddings:
                        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                    # fixes for #522 and #487 to avoid oom problems on gpu with large datasets
                    if convert_to_numpy:
                        embeddings = embeddings.cpu()

                all_embeddings.extend(embeddings)

        all_embeddings = [all_embeddings[idx] for idx in np.argsort(length_sorted_idx)]

        if convert_to_tensor:
            all_embeddings = torch.stack(all_embeddings)
        elif convert_to_numpy:
            all_embeddings = np.asarray([emb.numpy() for emb in all_embeddings])

        if input_was_string:
            all_embeddings = all_embeddings[0]

        return all_embeddings    
    def batch_to_device(batch, target_device: device):
        """
        send a pytorch batch to a device (CPU/GPU)
        """
        for key in batch:
            if isinstance(batch[key], Tensor):
                batch[key] = batch[key].to(target_device)
        return batch
        
        
    def snapshot_download(
        repo_id: str,
        revision: Optional[str] = None,
        cache_dir: Union[str, Path, None] = None,
        library_name: Optional[str] = None,
        library_version: Optional[str] = None,
        user_agent: Union[Dict, str, None] = None,
        ignore_files: Optional[List[str]] = None,
        use_auth_token: Union[bool, str, None] = None
    ) -> str:
        """
        Method derived from huggingface_hub.
        Adds a new parameters 'ignore_files', which allows to ignore certain files / file-patterns
        """
        if cache_dir is None:
            cache_dir = HUGGINGFACE_HUB_CACHE
        if isinstance(cache_dir, Path):
            cache_dir = str(cache_dir)

        _api = HfApi()
        
        token = None 
        if isinstance(use_auth_token, str):
            token = use_auth_token
        elif use_auth_token:
            token = HfFolder.get_token()
            
        model_info = _api.model_info(repo_id=repo_id, revision=revision, token=token)

        storage_folder = os.path.join(
            cache_dir, repo_id.replace("/", "_")
        )

        all_files = model_info.siblings
        #Download modules.json as the last file
        for idx, repofile in enumerate(all_files):
            if repofile.rfilename == "modules.json":
                del all_files[idx]
                all_files.append(repofile)
                break

        for model_file in all_files:
            if ignore_files is not None:
                skip_download = False
                for pattern in ignore_files:
                    if fnmatch.fnmatch(model_file.rfilename, pattern):
                        skip_download = True
                        break

                if skip_download:
                    continue

            url = hf_hub_url(
                repo_id, filename=model_file.rfilename, revision=model_info.sha
            )
            relative_filepath = os.path.join(*model_file.rfilename.split("/"))

            # Create potential nested dir
            nested_dirname = os.path.dirname(
                os.path.join(storage_folder, relative_filepath)
            )
            os.makedirs(nested_dirname, exist_ok=True)

            cached_download_args = {'url': url,
                'cache_dir': storage_folder,
                'force_filename': relative_filepath,
                'library_name': library_name,
                'library_version': library_version,
                'user_agent': user_agent,
                'use_auth_token': use_auth_token}

            if version.parse(huggingface_hub.__version__) >= version.parse("0.8.1"):
                # huggingface_hub v0.8.1 introduces a new cache layout. We sill use a manual layout
                # And need to pass legacy_cache_layout=True to avoid that a warning will be printed
                cached_download_args['legacy_cache_layout'] = True

            path = cached_download(**cached_download_args)

            if os.path.exists(path + ".lock"):
                os.remove(path + ".lock")

        return storage_folder
    

    
    def _load_auto_model(self, model_name_or_path):
        """
        Creates a simple Transformer + Mean Pooling model and returns the modules
        """
        logger.warning("No sentence-transformers model found with name {}. Creating a new one with MEAN pooling.".format(model_name_or_path))
        transformer_model = Transformer(model_name_or_path)
        pooling_model = Pooling(transformer_model.get_word_embedding_dimension(), 'mean')
        return [transformer_model, pooling_model]

    def _load_sbert_model(self, model_path):
        """
        Loads a full sentence-transformers model
        """
        # Check if the config_sentence_transformers.json file exists (exists since v2 of the framework)
        config_sentence_transformers_json_path = os.path.join(model_path, 'config_sentence_transformers.json')
        if os.path.exists(config_sentence_transformers_json_path):
            with open(config_sentence_transformers_json_path) as fIn:
                self._model_config = json.load(fIn)

            if '__version__' in self._model_config and 'sentence_transformers' in self._model_config['__version__'] and self._model_config['__version__']['sentence_transformers'] > __version__:
                logger.warning("You try to use a model that was created with version {}, however, your version is {}. This might cause unexpected behavior or errors. In that case, try to update to the latest version.\n\n\n".format(self._model_config['__version__']['sentence_transformers'], __version__))

        # Check if a readme exists
        model_card_path = os.path.join(model_path, 'README.md')
        if os.path.exists(model_card_path):
            try:
                with open(model_card_path, encoding='utf8') as fIn:
                    self._model_card_text = fIn.read()
            except:
                pass

        # Load the modules of sentence transformer
        modules_json_path = os.path.join(model_path, 'modules.json')
        with open(modules_json_path) as fIn:
            modules_config = json.load(fIn)

        modules = OrderedDict()
        for module_config in modules_config:
            module_class = self.import_from_string(module_config['type'])
            module = module_class.load(os.path.join(model_path, module_config['path']))
            modules[module_config['name']] = module

        return modules
    
        
    def import_from_string(dotted_path):
        """
        Import a dotted module path and return the attribute/class designated by the
        last name in the path. Raise ImportError if the import failed.
        """
        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
        except ValueError:
            msg = "%s doesn't look like a module path" % dotted_path
            raise ImportError(msg)

        try:
            module = importlib.import_module(dotted_path)
        except:
            module = importlib.import_module(module_path)

        try:
            return getattr(module, class_name)
        except AttributeError:
            msg = 'Module "%s" does not define a "%s" attribute/class' % (module_path, class_name)
            raise ImportError(msg)





class GPTEmbeddings:
    client: Any  #: :meta private:
    model_name: str = DEFAULT_MODEL_NAME
    """Model name to use."""
    cache_folder: Optional[str] = None
    """Path to store models. 
    Can be also set by SENTENCE_TRANSFORMERS_HOME environment variable."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Key word arguments to pass to the model."""
    encode_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Key word arguments to pass when calling the `encode` method of the model."""
    def __init__(self, **kwargs: Any):
        self.api_key = os.getenv("OPENAI_API_KEY")
        super().__init__(**kwargs)
        try:
            import sentence_transformers
        except ImportError as exc:
            raise ImportError(
                "Could not import sentence_transformers. "
            ) from exc
        
        self.client = SentenceTransformer(self.model_name, cache_folder=self.cache_folder, **self.model_kwargs)

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid



    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        embeddings = self.client.encode(texts, **self.encode_kwargs)
#        response = requests.post("https://api.openai.com/v1/embeddings", data={"input": text, "model":"text-embedding-ada-002"}, headers={"Authorization": "Bearer " + self.api_key}).json()
        print(embeddings)
        return embeddings.tolist()
    
        
    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        text = text.replace("\n", " ")
        embedding = self.client.encode(text, **self.encode_kwargs)
        return embedding.tolist()
