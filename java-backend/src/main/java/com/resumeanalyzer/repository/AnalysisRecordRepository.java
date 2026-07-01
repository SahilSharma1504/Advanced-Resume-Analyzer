package com.resumeanalyzer.repository;

import com.resumeanalyzer.entity.AnalysisRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnalysisRecordRepository extends JpaRepository<AnalysisRecord, Long> {

    // Spring Data JPA custom derived query
    List<AnalysisRecord> findByUsernameOrderByTimestampAsc(String username);
}
