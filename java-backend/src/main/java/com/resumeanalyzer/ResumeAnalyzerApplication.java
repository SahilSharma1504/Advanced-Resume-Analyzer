package com.resumeanalyzer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.annotation.Bean;
import org.springframework.context.event.EventListener;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class ResumeAnalyzerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ResumeAnalyzerApplication.class, args);
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @EventListener(ApplicationReadyEvent.class)
    public void onStartup() {
        try {
            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.getForEntity("http://127.0.0.1:5000/api/test-llm",
                    String.class);
            if (response.getStatusCode().is2xxSuccessful()) {
                System.out.println("Python AI service connected");
            } else {
                System.err.println("WARNING: Python AI service returned non-200 status");
            }
        } catch (Exception e) {
            System.err.println("WARNING: Python AI service not running");
        }
    }
}
