package com.resumeanalyzer.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // Allow localhost frontend access
public class ResumeController {

    private final String PYTHON_BASE_URL = "http://127.0.0.1:5000/api";

    @Autowired
    private RestTemplate restTemplate;

    /*
     * =========================================================================
     * MICROSERVICE EXPLANATION (For Viva/Academic Purposes):
     * =========================================================================
     * This Java Spring Boot application acts as the "API Gateway" in our
     * microservice architecture.
     * 
     * Why is this used?
     * 1. Separation of Concerns: Java is excellent at handling concurrent web
     * requests, security, and routing.
     * 2. Python is excellent at heavy NLP (Natural Language Processing) and AI
     * tasks.
     * 
     * How it works:
     * - The Frontend (HTML/JS) sends requests to THIS Java Controller.
     * - This Java Controller packages the files/data into JSON or Multipart
     * requests.
     * - It forwards the request to the Python microservice using Spring's
     * RestTemplate.
     * - It receives the AI output and sends it back to the client.
     * =========================================================================
     */

    @PostMapping("/analyze-advanced")
    public ResponseEntity<String> analyzeResumeAdvanced(
            @RequestParam("resume") MultipartFile file) {

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

            ByteArrayResource fileAsResource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };

            body.add("resume", fileAsResource);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    PYTHON_BASE_URL + "/analyze-advanced",
                    requestEntity,
                    String.class);

            return ResponseEntity.status(response.getStatusCode()).body(response.getBody());

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError()
                    .body("{\"error\": \"Error communicating with AI Microservice: " + e.getMessage() + "\"}");
        }
    }

    @PostMapping("/chat")
    public ResponseEntity<String> chatAssistant(@RequestBody Map<String, Object> payload) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(payload, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    PYTHON_BASE_URL + "/chat",
                    requestEntity,
                    String.class);
            return ResponseEntity.status(response.getStatusCode()).body(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("{\"error\": \"Chatbot offline.\"}");
        }
    }

    @PostMapping("/improve")
    public ResponseEntity<String> improveBullet(@RequestBody Map<String, Object> payload) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(payload, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    PYTHON_BASE_URL + "/improve",
                    requestEntity,
                    String.class);
            return ResponseEntity.status(response.getStatusCode()).body(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("{\"error\": \"Bullet improver offline.\"}");
        }
    }

    @PostMapping("/quick-score")
    public ResponseEntity<String> quickScore(@RequestBody Map<String, Object> payload) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(payload, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    PYTHON_BASE_URL + "/quick-score",
                    requestEntity,
                    String.class);
            return ResponseEntity.status(response.getStatusCode()).body(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("{\"error\": \"Quick score offline.\"}");
        }
    }

    /**
     * @apiNote GET /api/health
     *          Microservice monitoring endpoint to ensure the API Gateway is
     *          running.
     *          Required for completing the project requirements.
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "Java API running");
        return ResponseEntity.ok(response);
    }
}
