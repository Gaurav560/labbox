package com.setu;

/** Setu, described as a Java interface. LangChain4j writes the implementation. */
public interface Assistant {

    // TODO (task system_annotation): give Setu its instructions with an annotation on this method:
    //   @SystemMessage(fromResource = "setu-system.txt") (the file is in src/main/resources).
    String chat(String question);
}
