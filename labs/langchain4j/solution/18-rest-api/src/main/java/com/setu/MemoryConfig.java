package com.setu;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;

/** A chat memory per passenger: the starter gives this bean to every @AiService automatically. */
@Configuration
public class MemoryConfig {

    @Bean
    ChatMemoryProvider chatMemoryProvider() {
        return passenger -> MessageWindowChatMemory.builder().id(passenger).maxMessages(10).build();
    }
}
