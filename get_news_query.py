import openai
import faiss
import numpy as np
import pickle
from tqdm import tqdm
import argparse
import  os
import pandas as pd
openai.api_key = "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"
def create_embeddings(input):
    """Create embeddings for the provided input."""
    result = []
    # limit about 1000 tokens per request
    input = [str(text) for text in input if isinstance(text, (str, int))]
    lens = [len(text) for text in input]
    query_len = 0
    start_index = 0
    tokens = 0

    def get_embedding(input_slice):
        embedding = openai.Embedding.create(model="text-embedding-ada-002", input=input_slice)
        return [(text, data.embedding) for text, data in zip(input_slice, embedding.data)], embedding.usage.total_tokens

    for  index , l  in  tqdm ( enumerate ( lens )):
        query_len += l
        if query_len > 4096:
            ebd, tk = get_embedding(input[start_index:index + 1])
            query_len = 0
            start_index = index + 1
            tokens += tk
            result.extend(ebd)

    if query_len > 0:
        ebd, tk = get_embedding(input[start_index:])
        tokens += tk
        result.extend(ebd)
    return result, tokens

def create_embedding(text):
    """Create an embedding for the provided text."""
    embedding = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    return text, embedding.data[0].embedding

class  QA ():
    def __init__(self,data_embe) -> None:
        d = 1536
        index = faiss.IndexFlatL2(d)
        embe  =  np . array ([ emm [ 1 ] for  emm  in  data_embe ])
        data = [emm[0] for emm in data_embe]
        index.add(embe)
        self.index = index
        self.data = data
    def __call__(self, query):
        embedding = create_embedding(query)
        context = self.get_texts(embedding[1], limit)
        answer = self.completion(query,context)
        return answer,context
    def get_texts(self,embeding,limit):
        _,text_index = self.index.search(np.array([embeding]),limit)
        context = []
        for  i  in  list ( text_index [ 0 ]):
            context.extend(self.data[i:i+5])
        # context = [self.data[i] for i in list(text_index[0])]
        return context
    
    def completion(self,query, context):
        """Create a completion."""
        lens = [len(text) for text in context]

        maximum = 3000
        for index, l in enumerate(lens):
            maximum -= l
            if maximum < 0:
                context = context[:index + 1]
                print ( "Exceeded the maximum length, truncated to the front" , index  +  1 , "segments" )
                break

        text = "\n".join(f"{index}. {text}" for index, text in enumerate(context))
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {'role': 'system',
                'content' : f'You are a helpful AI article assistant, extract useful content from the following to answer, you cannot answer the content that is not mentioned below, and the relevance is sorted from high to low: \n \ n { text } ' },
                {'role': 'user', 'content': query},
            ],
        )
        print ( "tokens used: " , response . usage . total_tokens )
        return response.choices[0].message.content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Document QA")
    parser . add_argument ( "--input_file" , default = "bbc-sport2.xlsx" , dest = "input_file" , type = str , help = "input file path" )
    parser . add_argument ( "--file_embeding" , default = "input_embed.pkl" , dest = "file_embeding" , type = str , help = "file path of file embeding" )
    parser . add_argument ( "--print_context" , action = 'store_true' , help = "whether to print context" )

    args = parser.parse_args()

    # if os.path.isfile(args.file_embeding):
    #     data_embe = pickle.load(open(args.file_embeding,'rb'))
    # else:
    #     with open(args.input_file,'r',encoding='utf-8') as f:
    #         texts = f.readlines()
    #         texts = [text.strip() for text in texts if text.strip()]
    #         data_embe,tokens = create_embeddings(texts)
    #         pickle.dump(data_embe,open(args.file_embeding,'wb'))
    #         print ( "Text consumes {} tokens" . format ( tokens ))
    args = parser.parse_args()

    if os.path.isfile(args.file_embeding):
        data_embed = pickle.load(open(args.file_embeding, 'rb'))
    else:
        # Read data from Excel file using pandas
        data_frame = pd.read_excel(args.input_file)
        print(data_frame)
        # Calculate the index to split the data into half
        split_index = len(data_frame) // 2

        # Extract columns from the data_frame
        img_link = data_frame['ImageLink'].tolist()[:split_index]  # First half of ImageLink
        heading = data_frame['Heading'].tolist()[:split_index]
        subheading = data_frame['Subheading'].tolist()[:split_index]

        # Create embeddings for the texts (your implementation)
        data_embed, tokens = create_embeddings(img_link + heading + subheading)
        # article_links = data_frame['article_links'].tolist()
        # article = data_frame['article'].tolist()

        # Create embeddings for the texts (your implementation)
        data_embed, tokens = create_embeddings(img_link + heading + subheading)

        # Save the embeddings to a pickle file
        pickle.dump(data_embed, open(args.file_embeding, 'wb'))

        print("Text consumes {} tokens".format(tokens))

    qa = QA(data_embed)

    limit = 10
    while True:
        query = input("Please enter a query (help can view instructions): ")
        if query == "quit":
            break
        elif query.startswith("limit"):
            try:
                limit = int(query.split(" ")[1])
                print("limit is set to", limit)
            except Exception as e:
                print("Failed to set limit", e)
            continue
        elif query == "help":
            print("Enter limit [number] to set limit")
            print("Enter quit to exit")
            continue
        answer, context = qa(query)

        # Calculate the available space for the response
        max_response_length = 8191 - len(query)  # Adjust as needed

        # Truncate answer and context if they are too long
        if len(answer) > max_response_length:
            answer = answer[:max_response_length]

        if len(context) > max_response_length:
            context = context[:max_response_length]

        if args.print_context:
            # Print the truncated context
            print("Related fragment found:")
            for text in context:
                print('\t', text)
            print("=====================================")

        print("The answer is as follows\n\n")
        print(answer.strip())
        print("=====================================")
