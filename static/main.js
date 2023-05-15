var cart = [];

function addToCart(itemId, itemName, itemImage, itemPrice) {
    // check if item already exists in cart
    for (var i = 0; i < cart.length; i++) {
        if (cart[i].id == itemId) {
        // item already exists, update quantity
        cart[i].quantity += 1;
        updateCart();
        return;
        }
    }

    // item doesn't exist in cart, add it
    cart.push({
        id: itemId,
        name: itemName,
        image: itemImage,
        price: itemPrice,
        quantity: 1
    });

    updateCart();
    }

    function updateCart() {
    var total = 0;
    var cartHTML = '<ul>';
    for (var i = 0; i < cart.length; i++) {
        total += parseFloat(cart[i].price) * cart[i].quantity;
        cartHTML += '<li>';
        if (cart[i].image) {
        cartHTML += '<img src="/static/images/' + cart[i].image + '" alt="' + cart[i].name + '"> ';
        }
        cartHTML += cart[i].name + ' - $' + cart[i].price + ' x ' + cart[i].quantity + '</li>';
    }
    cartHTML += '</ul>';
    cartHTML += '<p>Total: $' + total.toFixed(2) + '</p>';

    document.getElementById("cart").innerHTML = "Cart: " + cart.length + " items" + cartHTML;
    }