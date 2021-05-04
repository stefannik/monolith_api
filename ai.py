from requests.api import get
import torch
from pytorch_transformers import BertTokenizer
from pytorch_transformers import BertModel
from torch import nn, optim, tensor, cuda, save
import numpy as np
import timeit


start = timeit.default_timer()


def get_embedding(text, n_tokens):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased',output_hidden_states=True)

    start = tokenizer.tokenize("[CLS]")
    end = tokenizer.tokenize("[SEP]")
    padding = tokenizer.tokenize("[PAD]")
    tokenized_text = tokenizer.tokenize(text)

    non_tag_tokens = n_tokens-2
    last_token_id = n_tokens-1

    n_pads = non_tag_tokens-len(tokenized_text)
    tokenized_text = start + padding*n_pads + tokenized_text 
    tokenized_text = tokenized_text[:last_token_id] + end

    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    tokens_tensor = torch.tensor([indexed_tokens])

    # segments_ids = [1] * len(tokenized_text)
    # segments_tensors = torch.tensor([segments_ids])

    model.eval()

    with torch.no_grad():
        outputs = model(tokens_tensor)
        # outputs = model(tokens_tensor, segments_tensors)
        last_hidden_state = outputs[0]
        word_embed_1 = last_hidden_state
        vectors = word_embed_1.cpu().numpy()[0]
        return vectors


class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        # x input shape => (batch_size, sequence, features) or (number_of_examples, length_of sequence, num_features)
        self.output_layer = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        hidden_state_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        # Initial hidden state (num_layers, batch_size, hidden_size (number of neurons per layer))
        rnn_output, _ = self.rnn(x, hidden_state_0)
        # Output features of the last layer of the RNN (the _ is for only getting the hidden_state of a n step of sequence, we don't need it)
        # rnn_output size => (batch_size, seq_length, hidden_size) (n, 20, 128)
        rnn_output_last_step = rnn_output[:, -1, :]     # filter only last step: (n, 128)
        # Feed the the linear output layer the last step and get its classification
        classification_output = self.output_layer(rnn_output_last_step)
        return classification_output


def score(text, model):
    if model == "sense":
        # cat 0 == factual, cat 1 == sensationalistic
        sequence_length, hidden_size, cat = 34, 1024, 0
        model_file = "models/sense_torch_gru34_1024x2_epoch_6"
        vectors = get_embedding(text, 34)
    elif model == "portada":
        # cat 0 == interior pages, cat 1 == frontpage
        sequence_length, hidden_size, cat = 54, 1536, 1
        model_file = "models/ny_torch_gru54_1536x2_epoch_13"
        vectors = get_embedding(text, 54)
    else:
        raise Exception("The model name is not valid. It must be 'sense' or 'portada'")
    
    input_size = 768
    num_layers = 2
    num_classes = 2

    model = RNN(input_size, hidden_size, num_layers, num_classes)

    model.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))
    model.eval()

    seq = np.array(vectors).reshape(-1, sequence_length, input_size)
    seq = torch.from_numpy(seq)

    prediction = model(seq)

    probabilities = torch.nn.Sigmoid()(prediction).detach().numpy()[0]
    # predicted_cat = torch.argmax(prediction)
    return probabilities[cat]


# sample = "High School Coach Fired After Refusing To Enforce Insane Outdoor Masks During Sports"
# sample_sense_score = score(sample, 'sense')
# sample_portada_score = score(sample, 'portada')
# print(sample_sense_score)
# print(sample_portada_score)
