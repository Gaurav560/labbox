package com.shop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "shop")
public record ShopProperties(String name, int freeDeliveryAbovePaise) {
}
