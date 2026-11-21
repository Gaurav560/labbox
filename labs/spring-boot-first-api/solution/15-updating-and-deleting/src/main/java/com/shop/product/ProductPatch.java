package com.shop.product;

/**
 * The body of a PATCH: only the fields to change. Integer (not int) so a missing field is null, which means
 * "leave it as it is". With int, a missing field would be 0, and you could not tell "not sent" from "zero".
 */
public record ProductPatch(String name, Integer pricePaise, Integer stock) {
}
