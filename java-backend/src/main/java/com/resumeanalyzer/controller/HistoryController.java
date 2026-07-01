package com.resumeanalyzer.controller;

import com.resumeanalyzer.entity.AnalysisRecord;
import com.resumeanalyzer.repository.AnalysisRecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/history")
@CrossOrigin(origins = "*")
public class HistoryController {

    @Autowired
    private AnalysisRecordRepository repository;

    @PostMapping("/save")
    public ResponseEntity<?> saveHistory(@RequestBody Map<String, Object> payload) {
        try {
            String username = (String) payload.getOrDefault("username", "Guest");
            // If the user didn't type a username, don't save history
            if (username == null || username.trim().isEmpty() || username.equalsIgnoreCase("Guest")) {
                return ResponseEntity.ok().body("{\"message\": \"Skipped saving for Guest.\"}");
            }

            int overall = (Integer) payload.getOrDefault("overall_score", 0);
            int quality = (Integer) payload.getOrDefault("quality_score", 0);
            int exp = (Integer) payload.getOrDefault("experience_score", 0);
            int ats = (Integer) payload.getOrDefault("ats_score", 0);

            AnalysisRecord record = new AnalysisRecord(username, overall, quality, exp, ats);
            repository.save(record);

            return ResponseEntity.ok().body("{\"message\": \"History saved successfully.\"}");
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("{\"error\": \"Could not save history.\"}");
        }
    }

    @GetMapping("/{username}")
    public ResponseEntity<?> getHistory(@PathVariable String username) {
        try {
            List<AnalysisRecord> history = repository.findByUsernameOrderByTimestampAsc(username);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("{\"error\": \"Could not fetch history.\"}");
        }
    }
}
