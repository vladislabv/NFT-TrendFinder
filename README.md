# NFT-TrendFinder
This repository serves for the final project of the course ([link](https://github.com/vitekzkytek/PythonDataIES))

The aim of the project is to reveal trendy characteristics of NFT Images on the second largest market pratform: ([link](https://rarible.com/))

The project is using a DALLE-Model, which was trained on 2000 NFT images, obtained from the API. The tools for model training were provided by: ([link](https://github.com/lucidrains/DALLE-pytorch/))

Supervisor: Martin Hronec

What the project does?
1. NFT_TrendFinder collects the characteristics of the most expensive images from the NFT marketplace - Rarible ([link](https://rarible.com/)) in text format, passes them to the neural network - DALL-E ([link](https://openai.com/blog/dall-e/)), so that it produces new works of art. 
2. It shows the necessary for customers statistics, like:
- "Most expensive NFTs": determines the most expensive NFT along with characteristics - price, date of creation, description, artist
- "Characteristics of most expensive NFTs": using Meta (Key, Value) data to accumulate characteristics of top by price images in the text format
- "Making pairs of characteristics to fulfill description": preparing a text database with pairs of "trend" descriptions from previous point for a complete description

Technical perspective:
- The project is a flask web application, containing python/javascript scripts in backend, html/css in frontend
- The app uses MongoDB for storing data, being fetched form the NFT Rarible platform, since it is most useful form for storing unstructured data
- NFT-TrendFinder is an asyncrously built application, using Celery (with RabbitMQ as Message Broker and MongoDB as storage for task messages) tasks

Why the project is useful?
The crypto-art industry is growing exponentially. This is facilitated by the strengthening of the organic union between human and machine, which involves the development of gamification and decoration of the virtual space as a whole. The fact that we are entering a new rapidly developing era does not mean at all that people are adjusting to its requirements just as quickly. So if a company or an individual user wants to keep up with the times - by that we mean quick earnings from trading on NFT marketplaces OR search for contemporary high-level artists and styles - but do not have an artistic background --- our NFT_TrendFinder will be able to lend them a helping hand by giving them a finished NFT and actual information about the market. Which will help them not to waste time on drawing and designing pictures and researching the marketplace.

Prerequisites:
- Docker and Docker Compose: ([link](https://docs.docker.com/compose/install/)); Also check the system requirements before installing the software
- Free Space for the project - initially it will require about 14 GBs, but the app will grow since it collects data from the API source given above. (recommended to have > 50GBs in total)
- Some patience until the app is compiled, it requires about 20-30 Minutes to compile, depends on your current internet connection. We can guarantee 20 Minutes, if your interenet speed is above 80 MBs/s

How to compile the project?
- Since the docker provide great user excepience in complex projects, everything you will need to do is clone this repository locally and compile the docker container.
- After the project is cloned and your Docker is up, only one command inside the repo is required: `docker-compose up --build`
- After some time you can access the web application under `localhost:5000/home`, which is the main page.
- Besides the main application, you can also access RabbitMQ-Management (`localhost:15672`) app and Mongo-Express (`localhost:8081`), which is a nice web app for inspecting data in the MongoDB

How to use this?
1. On the website, you need to construct your data insights, which can be done in `Constructor` section;
2. There, you will be asked to specify start and end date for analysing, and the number of documents to show as the result, consider that 50 is recommended maximal number in order to provide time efficient query fetching;
3. After the job is done, you will be asked to be redirected to the showpage, where you can observe the customer statistics based on your preferences;
4. At the end, you can also choose characterics to put for image generation. Under the hood, your text will be feed to the DALLE-Model and you will be able to download obtained output picture;

Further development:
- Since the application provides great to work with NFT characteristics, interested researcher can supplement the project with new APIs or services, where the relevant data may come from.
- Besides, the model was trained on few images, you can improve it by training better DALLE Model or use some pretrained instead for generating NFTs.
- We find it is a good idea, to train another model, which will be able to predict NFT prices, by using this, the users can get a fair "start price" for their generated NFTs :)

Cautions:
- By generating pictures, you will see that images are 128x128 pixels, however we could achieve 512x512 images generated by DALLE. The problem can be solved by including GPU memory to the docker, which part is commented in `Dockerfile`. The pretrained model for this lies also in the Public directory of the MyDrive Cloud: ([link](https://drive.google.com/file/d/1YK-xOaxNuH7IXVBinn1Oqd-qIUInVA7k/view?usp=sharing). Therefore, if you have enough NVIDIA GPU (> 6 GB), you could replace the pretrained checkpoints for the project. 
- Sometimes, you may experience some problems by generating NFTs, in those cases, just try some more times.

Who maintains and contributes to the project?
Alla Borodina & Vladislav Stasenko, further community is highly welcome!
