# MicroMob - Charity EV Auction

🚀 Project Objective:

The goal of the project is to create a platform to manage a charitable auction of electric vehicles. 
The technology stack involves the utilization of Django and DB Sql for the auction items, Redis (a NoSQL database) to manage the bid auction, and the Ethereum Blockchain Testnet Goerli to write on chain the result of each auction.

🔹 Key Requirements:

- Design a user-friendly bidding mechanism, enabling participants to bid on any auction active;
- Implement a very fast database to manage the various bids, such as Redis, and then store the outcome of the auction, like all other user data, in a relational database;
- Development of an auction posting and creation interface accessible only for the Admin user;
- Implementation of write on blockchain procedure in order to archive information for concluded auctions with all the relative informations.

💻 Implemented Features:

The project incorporates an array of functionalities designed to enhance user experience:

- Formulated registration and login forms for user;
- Dedicated page, restricted to the Admin, for creation and posting new auction;
- Crafting a publicly accessible page showcasing currently active auctions and already closed auction;
- Design a dedicate page to allows users to participate and bidding for the ongoing auctions;
- Dedicate page, restricted to user logged, where find the auction won;

💻 Deployment:

To deploy this project (Mac OS Version):
- Create a Virtual Environment

```bash
  python3 -m venv venv
```
```bash
  source venv/bin/activate
```

- Clone the repo and install requirements in ethweb3/requirements.txt

```bash
  pip install -r requirements.txt
```

- Use the folder "app":

```bash
  cd app
```
- Make database migrations
```bash
  python manage.py makemigrations
```
```bash
  python manage.py migrate
```
- Run 
```bash
  python manage.py runserver
```

## 🛠 Skills
Django, Redis, Python, HTML, CSS, Web3, ETH, Goerli Testnet

## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/foschimatteo/)