package com.shop.config;

// TODO (task shop_properties): bind the settings under "shop" in application.yml to this record, with
// @ConfigurationProperties. (ShopApiApplication already has @ConfigurationPropertiesScan.)
public record ShopProperties(String name, int freeDeliveryAbovePaise) {
}
