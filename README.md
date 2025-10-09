The main file for this project is the ANLPHW2.ipynb. The notebook was ran on Colab using a T4 GPU and high RAM.
The cells are in logical order, starting with a github repo clone (all the scraped data and testing data is pulled in that way). Then necessary packages are installed.
In order to run the model, the user has to request access from Meta to use the llama-3-8b-instruct model. Once given access the file will run
The next cell loads the llama-3-8b-instruct model from Meta. This is a gated repo on huggingface that requires the user to agree to the Meta user agreement.
The pararmeters to the model can be adjusted in multiple locations. 
Within the rag function the user can adjust the hybrid weighted average alpha, the dense and sparse noramlizers, and the whether to include a chunk threshold or not. 
If you want to change the threshold itself, you must adjust it in the weighted_average_hybrid function.
Within the evaluate_rag function the rag function is called. That is where I would change how many chunks to retain (k= 3, 4, etc.)
I change the the system prompt passed to the model in the cell after the cell where evaluate_rag is declared by passing it to the function.
