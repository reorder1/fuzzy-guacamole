'use client';

import { useParams } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Button, Form, Table } from 'react-bootstrap';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface Scan {
  id: number;
  status: string;
  extracted_student_number: string;
  extracted_set_code: string;
  answers: string[];
  issues: string[];
}

interface Student {
  id: number;
  student_number: string;
  full_name: string;
}

export default function ReviewPage() {
  const params = useParams<{ id: string }>();
  const examId = params.id;
  const [selected, setSelected] = useState<Scan | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [overlayUrl, setOverlayUrl] = useState<string | null>(null);

  const scansQuery = useQuery({
    queryKey: ['scans', examId, 'review'],
    queryFn: async () => {
      const res = await api.get('/scans/', { params: { exam: examId } });
      return res.data as Scan[];
    }
  });

  useEffect(() => {
    api.get('/students/').then((res) => setStudents(res.data));
  }, []);

  useEffect(() => {
    if (!selected) {
      setOverlayUrl(null);
      return;
    }
    api
      .get(`/scans/${selected.id}/overlay/`, { responseType: 'blob' })
      .then((res) => {
        setOverlayUrl(URL.createObjectURL(res.data));
      })
      .catch(() => setOverlayUrl(null));
  }, [selected]);

  const reviewMutation = useMutation({
    mutationFn: async (payload: { student: number; set_code: string; answers: string[] }) => {
      if (!selected) return;
      await api.post(`/scans/${selected.id}/review/`, payload);
    },
    onSuccess: () => {
      setSelected(null);
      scansQuery.refetch();
    }
  });

  return (
    <Layout>
      <h1>Review Queue</h1>
      <Table bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Student</th>
            <th>Issues</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {scansQuery.data
            ?.filter((scan) => scan.status !== 'processed')
            .map((scan) => (
              <tr key={scan.id}>
                <td>{scan.id}</td>
                <td>{scan.status}</td>
                <td>{scan.extracted_student_number}</td>
                <td>{scan.issues.join(', ')}</td>
                <td>
                  <Button size="sm" onClick={() => setSelected(scan)}>
                    Review
                  </Button>
                </td>
              </tr>
            ))}
        </tbody>
      </Table>

      {selected && (
        <div className="d-flex gap-4">
          <div>
            <h2>Overlay</h2>
            {overlayUrl ? <img src={overlayUrl} alt="overlay" style={{ maxWidth: 400 }} /> : <p>No overlay available</p>}
          </div>
          <div style={{ minWidth: 320 }}>
            <h2>Correction</h2>
            <Form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget as HTMLFormElement);
                const studentId = Number(formData.get('student'));
                const setCode = String(formData.get('set_code'));
                const answers = String(formData.get('answers') || '')
                  .split(',')
                  .map((x) => x.trim().toUpperCase());
                reviewMutation.mutate({ student: studentId, set_code: setCode, answers });
              }}
            >
              <Form.Group className="mb-3">
                <Form.Label>Student</Form.Label>
                <Form.Select name="student" defaultValue="">
                  <option value="" disabled>
                    Select student
                  </option>
                  {students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.student_number} - {student.full_name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Set Code</Form.Label>
                <Form.Control name="set_code" defaultValue={selected.extracted_set_code || 'A'} />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Answers (comma separated)</Form.Label>
                <Form.Control name="answers" defaultValue={(selected.answers || []).join(',')} />
              </Form.Group>
              <Button type="submit">Save</Button>
            </Form>
          </div>
        </div>
      )}
    </Layout>
  );
}
