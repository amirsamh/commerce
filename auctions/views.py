from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Category, Listing, User, Watchlist, Comment, Bid
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
    })


@login_required(login_url='login')
def closed(request):
    return render(request, "auctions/closed.html", {
        "listings": Listing.objects.all(),
        "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        if not request.POST["username"] or not request.POST["email"] or not request.POST["password"] or not request.POST["confirmation"]:
            return render(request, "auctions/register.html", {
                "message": "Please complete the form.",
                "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
            })

        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def new(request):
    data = Category.objects.all().values()
    categories = []
    for i in data:
        categories.append(i["category"])

    if request.method == "POST":
        if request.POST["title"] and request.POST["description"]:
            try:
                listing = Listing()
                listing.img = request.POST["img"]
                listing.title = request.POST["title"]
                listing.description = request.POST["description"]
                listing.category = request.POST["category"]
                listing.startbid = request.POST["startbid"]
                listing.creator = User.objects.get(pk=request.user.id)
                listing.save()
                success = "The listing was successfully created!"
                message = None
            except ValueError:
                message = "Please provide a number for the starting bid."
                success = None
        else: 
            message = "Please complete the form"
            success = None
    else:
        message = None
        success = None

    return render(request, "auctions/new.html", {
        "categories": categories,
        "message": message,
        "success": success,
        "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
    })


@login_required(login_url='login')
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.values(),
        "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
    })


@login_required(login_url='login')
def category(request, category):
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": Listing.objects.filter(category=category),
            "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
        })


@login_required(login_url='login')
def listing(request, listing):
    #check if item is already in watchlist
    def in_watchlist(watchlist):
        if watchlist:
            for item in watchlist:
                if listing == item["listing"]:
                    return True
        return False

    #check if the given bid is higher than other bids
    def is_greater(bid, bids, starting_bid):
        for i in bids:
            if bid <= i:
                return False
        if bid < starting_bid:
            return False
        return True

    #the status of the listing
    status = Listing.objects.filter(title=listing).values()[0]["is_active"]
    #the dictionary of all bids associated with the listing
    bids = Bid.objects.filter(item=listing).values()
    #saving bid amounts to a list
    amounts = []
    for i in bids:
        amounts.append(i["amount"])

    bidders = {}
    for bid in bids:
        bidders[bid["user"]] = bid["amount"]

    starting_bid = Listing.objects.filter(title=listing).values()[0]["startbid"]

    if User.objects.filter(pk=request.user.id).values()[0]["username"] == Listing.objects.filter(title=listing).values()[0]["creator"]:
        creator = True
    else:
        creator = False

    if request.method == "POST":
        if request.POST.get("amount"):
            try:
                user_bid = float(request.POST.get("amount"))
                if not amounts and user_bid > starting_bid:
                    bid = Bid()
                    bid.amount = request.POST.get("amount")
                    bid.item = request.POST.get("bid_item")
                    bid.user = User.objects.get(pk=request.user.id)
                    bid.save()
                    message = f"Successfully bid on {listing}"
                    alert = None

                elif is_greater(user_bid, amounts, starting_bid):
                    bid = Bid()
                    bid.amount = request.POST.get("amount")
                    bid.item = request.POST.get("bid_item")
                    bid.user = User.objects.get(pk=request.user.id)
                    bid.save()
                    message = f"Successfully bid on {listing}"
                    alert = None

                else:
                    alert = "Please enter a higher price."
                    message = None
            except ValueError:
                alert =  "Please enter a valid number."
                message = None
            

        elif request.POST.get("remove"):
            Watchlist.objects.filter(listing=request.POST["remove"],
            creator=User.objects.get(pk=request.user.id)).delete()
            message = "Successfully removed listing from your watchlist."
            alert = None

        elif request.POST.get("item"):
            watchlist = Watchlist()
            watchlist.listing = request.POST["item"]
            watchlist.creator = User.objects.get(pk=request.user.id)
            watchlist.save()
            message = "Successfully added listing to watchlist."
            alert = None

        elif request.POST.get("comment"):
            comment = Comment()
            comment.text = request.POST["comment"]
            comment.item = request.POST["name"]
            comment.writer = User.objects.get(pk=request.user.id)
            comment.save()
            message = "Comment was successfully posted."
            alert = None

        elif request.POST.get("close_bid"):
            if bidders:
                Listing.objects.filter(title=listing).update(is_active=False)
                winner = max(bidders, key=bidders.get)
                Listing.objects.filter(title=listing).update(winner=winner)
                message = "Successfully closed bid."
                alert = None
            else:
                message = None
                alert = "No bids yet. Can't close the autcion."
    else:
        message = None
        alert = None

    if bidders:
        minimum = bidders[min(bidders, key=bidders.get)]
        bid_count = len(bidders)
    else:
        minimum = starting_bid
        bid_count = 0

    if Listing.objects.filter(title=listing).values()[0]["winner"] == User.objects.filter(pk=request.user.id).values()[0]["username"]:
        is_winner = True
    else:
        is_winner = False

    comments =  Comment.objects.filter(item=listing).values()
    watchlist = Watchlist.objects.filter(creator=User.objects.get(pk=request.user.id)).values()
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.filter(title=listing).values()[0],
        "statement": in_watchlist(watchlist),
        "comments": comments,
        "message": message,
        "alert": alert,
        "creator": creator,
        "status": status,
        "bid_count": bid_count,
        "minimum": minimum,
        "is_winner": is_winner,
        "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
    })


@login_required(login_url='login')
def watchlist(request):
    if request.method == "POST" and request.POST.get("remove"):
        Watchlist.objects.filter(listing=request.POST["remove"], 
        creator=User.objects.get(pk=request.user.id)).delete()

    title = Watchlist.objects.filter(creator=User.objects.get(pk=request.user.id)).values()
    if title:
        listing_titles = []
        for i in title:
            listing_titles.append(i)

        data = []
        for i in listing_titles:
            data.append(Listing.objects.filter(title=i["listing"]).values())

        listings = []
        for i in data:
            listings.append(i[0])

        return render(request, "auctions/watchlist.html", {
            "listings": listings,
            "watchlist_count": Watchlist.objects.filter(creator="amirsam").count()
        })
    else:   
        return render(request, "auctions/watchlist.html")