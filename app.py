characters).")
        return redirect(url_for("home"))

    if quantity < 1 or quantity > 100:
        flash("Quantity must be between 1 and 100.")
        return redirect(url_for("home"))

    conn = get_db()

    try:
        conn.execute("BEGIN IMMEDIATE")

        product = conn.execute("""
            SELECT * FROM products WHERE id = ?
        """, (product_id,)).fetchone()

        if product is None:
            conn.rollback()
            flash("Product not found.")
        elif product["stock"] < quantity:
            conn.rollback()
            flash("Not enough stock available.")
        else:
            total = product["price"] * quantity

            conn.execute("""
                INSERT INTO orders
                (customer_name, product_id, quantity, total)
                VALUES (?, ?, ?, ?)
            """, (customer, product_id, quantity, total))

            conn.execute("""
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
            """, (quantity, product_id))

            conn.commit()
            flash(
                f"Order placed! Total: PHP {total:,.2f}"
            )

    except sqlite3.Error:
        conn.rollback()
        flash("Something went wrong. Please try again.")
    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/orders")
def view_orders():
    conn = get_db()
    orders = conn.execute("""
        SELECT orders.*, products.name AS product_name
        FROM orders
        JOIN products ON products.id = orders.product_id
        ORDER BY orders.id DESC
    """).fetchall()
    conn.close()

    return render_template("orders.html", orders=orders)


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
