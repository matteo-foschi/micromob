import redis

r = redis.Redis(host="127.0.0.1", port=6379, password="", db=0, decode_responses=True)


def place_bid(auction_id, bidder, bid_amount):
    r.zadd(f"auction:{auction_id}", {bidder: bid_amount})


auction_id = 3

place_bid(auction_id, "user1", 150)
place_bid(auction_id, "user2", 200)
place_bid(auction_id, "user3", 180)
place_bid(auction_id, "user4", 250)

# Retrieve the highest bid amount for the auction
highest_bid = r.zrevrange(f"auction:{auction_id}", 0, 0, withscores=True)
print(
    "Highest bid:", highest_bid[0][0]
)  # This will print the bidder with the highest bid amount
print("Bid amount:", highest_bid[0][1])  # This will print the highest
print(r.get(auction_id))
