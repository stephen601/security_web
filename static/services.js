function addToCart(itemId, itemName, itemPrice) {
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
        price: parseFloat(itemPrice).toFixed(2),
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
        cartHTML += cart[i].name + ' - $' + parseFloat(cart[i].price).toFixed(2) + ' x ' + cart[i].quantity + '</li>';
    }
    cartHTML += '</ul>';
    cartHTML += '<p>Total: $' + total.toFixed(2) + '</p>';

    document.getElementById("services-cart").innerHTML = "Services Cart: " + cart.length + " items" + cartHTML;
}
