package com.shop.check;

import java.io.File;

import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@SpringBootTest
@AutoConfigureMockMvc
class Ch02Check {
    @Autowired
    MockMvc mvc;

    /** The text of the first element with this name directly under the given parent. */
    static String child(Element parent, String name) {
        var nodes = parent.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            if (nodes.item(i) instanceof Element e && e.getTagName().equals(name)) {
                return e.getTextContent().trim();
            }
        }
        return "";
    }

    @Test
    void addActuator() {
        R.task("add_actuator", () -> {
            var r = mvc.perform(get("/actuator/health")).andReturn().getResponse();
            if (r.getStatus() == 200 && r.getContentAsString().contains("UP")) {
                R.pass("add_actuator", "One dependency, and Spring Boot added a whole new endpoint: that is a starter plus auto-configuration at work.");
            } else {
                R.fail("add_actuator", "GET /actuator/health does not answer yet. Add a dependency with artifactId spring-boot-starter-actuator to pom.xml.", "200 {\"status\":\"UP\"}", String.valueOf(r.getStatus()));
            }
        });
    }

    @Test
    void projectIdentity() {
        R.task("project_identity", () -> {
            Document pom = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new File("pom.xml"));
            Element project = pom.getDocumentElement();
            String artifact = child(project, "artifactId");
            Element build = (Element) project.getElementsByTagName("build").item(0);
            String finalName = build == null ? "" : child(build, "finalName");
            if (!"shop-api".equals(artifact)) {
                R.fail("project_identity", "The project's own artifactId (the one right under <groupId>com.shop</groupId>, not the parent's) should be shop-api.", "shop-api", artifact);
            } else if (!"shop-api".equals(finalName)) {
                R.fail("project_identity", "The <finalName> inside <build> decides the jar's file name: make it shop-api.", "shop-api", finalName);
            } else {
                R.pass("project_identity", "The project is called shop-api, and mvn package now builds target/shop-api.jar.");
            }
        });
    }
}
