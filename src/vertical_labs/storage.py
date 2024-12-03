"""Storage system for crew results."""

import json
import sqlite3
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

class ResultsStorage:
    """Stores and manages crew results."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the storage system.
        
        Args:
            db_path: Path to SQLite database (default: ./results.db)
        """
        self.db_path = db_path or "./results.db"
        self.logger = logging.getLogger(__name__)
        self._init_db()
        
    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    crew_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Create results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    result_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    result_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs (run_id)
                )
            """)
            
            # Create relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    metadata TEXT,
                    PRIMARY KEY (source_id, target_id, relationship_type),
                    FOREIGN KEY (source_id) REFERENCES results (result_id),
                    FOREIGN KEY (target_id) REFERENCES results (result_id)
                )
            """)
            
            conn.commit()
            
    def store_run(
        self,
        run_id: str,
        crew_type: str,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store a new run.
        
        Args:
            run_id: Unique run identifier
            crew_type: Type of crew
            workflow_id: Optional workflow identifier
            metadata: Optional metadata dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO runs (
                    run_id, workflow_id, crew_type, status,
                    started_at, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    workflow_id,
                    crew_type,
                    "running",
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()
            
    def update_run_status(
        self,
        run_id: str,
        status: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Update the status of a run.
        
        Args:
            run_id: Run identifier
            status: New status
            metadata: Optional metadata to update
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if metadata:
                # Merge with existing metadata
                cursor.execute(
                    "SELECT metadata FROM runs WHERE run_id = ?",
                    (run_id,)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    existing_metadata = json.loads(result[0])
                    existing_metadata.update(metadata)
                    metadata = existing_metadata
                    
            cursor.execute(
                """
                UPDATE runs
                SET status = ?,
                    completed_at = CASE WHEN ? IN ('completed', 'failed')
                                      THEN datetime('now')
                                      ELSE completed_at END,
                    metadata = CASE WHEN ? IS NOT NULL
                                   THEN ?
                                   ELSE metadata END
                WHERE run_id = ?
                """,
                (
                    status,
                    status,
                    json.dumps(metadata) if metadata else None,
                    json.dumps(metadata) if metadata else None,
                    run_id
                )
            )
            conn.commit()
            
    def store_result(
        self,
        run_id: str,
        result_type: str,
        content: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> str:
        """Store a result.
        
        Args:
            run_id: Run identifier
            result_type: Type of result (e.g., topic, pitch, content)
            content: Result content
            metadata: Optional metadata
            
        Returns:
            Result identifier
        """
        result_id = f"{run_id}_{result_type}_{datetime.now().timestamp()}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO results (
                    result_id, run_id, result_type, content,
                    created_at, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    run_id,
                    result_type,
                    json.dumps(content) if isinstance(content, dict) else content,
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()
            
        return result_id
        
    def store_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store a relationship between results.
        
        Args:
            source_id: Source result identifier
            target_id: Target result identifier
            relationship_type: Type of relationship
            metadata: Optional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO relationships (
                    source_id, target_id, relationship_type, metadata
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    source_id,
                    target_id,
                    relationship_type,
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()
            
    def get_run(self, run_id: str) -> Optional[Dict]:
        """Get information about a run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Dictionary with run information or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_id, workflow_id, crew_type, status,
                       started_at, completed_at, metadata
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return {
                "run_id": result[0],
                "workflow_id": result[1],
                "crew_type": result[2],
                "status": result[3],
                "started_at": result[4],
                "completed_at": result[5],
                "metadata": json.loads(result[6]) if result[6] else None
            }
            
    def get_results(
        self,
        run_id: Optional[str] = None,
        result_type: Optional[str] = None
    ) -> List[Dict]:
        """Get results matching criteria.
        
        Args:
            run_id: Optional run identifier to filter by
            result_type: Optional result type to filter by
            
        Returns:
            List of result dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT result_id, run_id, result_type, content,
                       created_at, metadata
                FROM results
                WHERE 1=1
            """
            params = []
            
            if run_id:
                query += " AND run_id = ?"
                params.append(run_id)
                
            if result_type:
                query += " AND result_type = ?"
                params.append(result_type)
                
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [
                {
                    "result_id": r[0],
                    "run_id": r[1],
                    "result_type": r[2],
                    "content": json.loads(r[3]) if r[3].startswith("{") else r[3],
                    "created_at": r[4],
                    "metadata": json.loads(r[5]) if r[5] else None
                }
                for r in results
            ]
            
    def get_related_results(
        self,
        result_id: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict]:
        """Get results related to a given result.
        
        Args:
            result_id: Result identifier
            relationship_type: Optional relationship type to filter by
            
        Returns:
            List of related result dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT r.result_id, r.run_id, r.result_type,
                       r.content, r.created_at, r.metadata,
                       rel.relationship_type, rel.metadata as relationship_metadata
                FROM results r
                JOIN relationships rel ON r.result_id = rel.target_id
                WHERE rel.source_id = ?
            """
            params = [result_id]
            
            if relationship_type:
                query += " AND rel.relationship_type = ?"
                params.append(relationship_type)
                
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [
                {
                    "result_id": r[0],
                    "run_id": r[1],
                    "result_type": r[2],
                    "content": json.loads(r[3]) if r[3].startswith("{") else r[3],
                    "created_at": r[4],
                    "metadata": json.loads(r[5]) if r[5] else None,
                    "relationship": {
                        "type": r[6],
                        "metadata": json.loads(r[7]) if r[7] else None
                    }
                }
                for r in results
            ]
            
    def export_workflow_results(self, workflow_id: str) -> Dict:
        """Export all results for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Dictionary with complete workflow results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all runs in the workflow
            cursor.execute(
                """
                SELECT run_id, crew_type, status, started_at,
                       completed_at, metadata
                FROM runs
                WHERE workflow_id = ?
                ORDER BY started_at
                """,
                (workflow_id,)
            )
            runs = cursor.fetchall()
            
            workflow_results = {
                "workflow_id": workflow_id,
                "runs": []
            }
            
            for run in runs:
                run_dict = {
                    "run_id": run[0],
                    "crew_type": run[1],
                    "status": run[2],
                    "started_at": run[3],
                    "completed_at": run[4],
                    "metadata": json.loads(run[5]) if run[5] else None,
                    "results": self.get_results(run_id=run[0])
                }
                workflow_results["runs"].append(run_dict)
                
            return workflow_results