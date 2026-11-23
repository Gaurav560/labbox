package com.setu.check;

import java.util.List;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;

import com.setu.Models;
import com.setu.Specialists;
import com.setu.Supervisor;

import dev.langchain4j.agentic.supervisor.SupervisorAgent;
import dev.langchain4j.model.chat.ChatModel;

class Ch29Check {

    static final FakeOpenAi FAKE = new FakeOpenAi();

    @AfterAll
    static void stop() { FAKE.stop(); }

    static ChatModel model() {
        return Models.chatModel(FAKE.baseUrl(), "k");
    }

    /** The fare agent's model asks for the fare tool once, then answers with the tool's result. */
    static FakeOpenAi.Reply fareAgentModel(String body) {
        return body.contains("\"role\":\"tool\"") || body.contains("\"role\" : \"tool\"")
                ? FakeOpenAi.Reply.text("420")
                : FakeOpenAi.Reply.tool("fare", "{\"destination\": \"Ratnagiri\"}");
    }

    @Test
    void toolAgent() {
        R.task("tool_agent", () -> {
            Specialists.FareAgent agent = Supervisor.fareAgent(model());
            if (agent == null) {
                R.fail("tool_agent", "Supervisor.fareAgent(model) returned null. Build it with AgenticServices.agentBuilder(Specialists.FareAgent.class), .chatModel(model), .tools(new RailTools()), .outputKey(\"fare\") and .build().");
                return;
            }
            FAKE.reset();
            FAKE.script = Ch29Check::fareAgentModel;
            int got;
            try {
                got = agent.fare("Ratnagiri");
            } catch (RuntimeException e) {
                R.fail("tool_agent", "The model asked for the fare tool, but the agent has no tools. Add .tools(new RailTools()) to its builder.");
                return;
            }
            List<String> offered = FakeOpenAi.tools(FAKE.chat(0));
            if (!offered.contains("fare")) {
                R.fail("tool_agent", "The agent's model was not offered the fare tool: add .tools(new RailTools()).", "[fare, nextDate]", offered.toString());
                return;
            }
            if (got != 420) {
                R.fail("tool_agent", "The tool said 420 and the model repeated it, so fare(\"Ratnagiri\") should return 420.", "420", String.valueOf(got));
                return;
            }
            R.pass("tool_agent", "An agent with a tool: it asks RailTools for the fare instead of guessing it.");
        });
    }

    @Test
    void supervisorAgent() {
        R.task("supervisor_agent", () -> {
            SupervisorAgent supervisor = Supervisor.supervisor(model());
            if (supervisor == null) {
                R.fail("supervisor_agent", "Supervisor.supervisor(model) returned null. Build it with AgenticServices.supervisorBuilder(), .chatModel(model), .subAgents(fareAgent(model), dateAgent(model)), .supervisorContext(CONTEXT), .responseStrategy(SupervisorResponseStrategy.SUMMARY) and .build().");
                return;
            }
            FAKE.reset();
            int[] plans = {0};
            FAKE.script = b -> {
                if (b.contains("You are a planner expert")) {
                    plans[0]++;
                    return FakeOpenAi.Reply.text(plans[0] == 1
                            ? "{\"agentName\": \"fare\", \"arguments\": {\"destination\": \"Ratnagiri\"}}"
                            : "{\"agentName\": \"done\", \"arguments\": {\"response\": \"Two adults to Ratnagiri pay Rs 840 in total.\"}}");
                }
                return fareAgentModel(b);
            };
            String got = supervisor.invoke("How much do 2 adults pay to Ratnagiri?");
            String plan = FAKE.chatRequests.get(0);
            if (!plan.contains("Finds the fare in rupees") || !plan.contains("Finds the date of the next")) {
                R.fail("supervisor_agent", "The supervisor's planner should be told about both agents: .subAgents(fareAgent(model), dateAgent(model)).");
                return;
            }
            if (!plan.contains("fare for ONE adult")) {
                R.fail("supervisor_agent", "The planner does not know that fares are for one adult, so it may give 2 adults the price of one. Add .supervisorContext(CONTEXT).");
                return;
            }
            if (plans[0] != 2 || FAKE.chatRequests.size() < 4) {
                R.fail("supervisor_agent", "The planner chose the fare agent, but it did not run. Pass the agents with .subAgents(fareAgent(model), dateAgent(model)).",
                        "plan, fare agent (2 calls), plan", FAKE.chatRequests.size() + " model calls");
                return;
            }
            if (!"Two adults to Ratnagiri pay Rs 840 in total.".equals(got)) {
                R.fail("supervisor_agent", "With the default strategy the answer is the last agent's raw result. Add .responseStrategy(SupervisorResponseStrategy.SUMMARY) to return the planner's summary.",
                        "Two adults to Ratnagiri pay Rs 840 in total.", String.valueOf(got));
                return;
            }
            R.pass("supervisor_agent", "The model planned the steps itself: call the fare agent, then answer with a summary. Pure agentic AI.");
        });
    }
}
