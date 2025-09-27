'use client';

import { useParams } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Button, Form, Table } from 'react-bootstrap';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface Scan {
  id: number;
  status: string;
  extracted_student_number: string;
  extracted_set_code: string;
  confidence: number;
}

export default function UploadPage() {
  const params = useParams<{ id: string }>();
  const examId = params.id;
  const [file, setFile] = useState<File | null>(null);

  const query = useQuery({
    queryKey: ['scans', examId],
    queryFn: async () => {
      const res = await api.get('/scans/', { params: { exam: examId } });
      return res.data as Scan[];
    }
  });

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) return;
      const formData = new FormData();
      formData.append('exam', examId);
      formData.append('image', file);
      await api.post('/scans/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    },
    onSuccess: () => {
      setFile(null);
      query.refetch();
    }
  });

  return (
    <Layout>
      <h1>Upload Scans</h1>
      <Form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
        className="d-flex gap-2 mb-3"
      >
        <Form.Control type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <Button type="submit">Upload</Button>
      </Form>
      <Table bordered>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Student</th>
            <th>Set</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((scan) => (
            <tr key={scan.id}>
              <td>{scan.id}</td>
              <td>{scan.status}</td>
              <td>{scan.extracted_student_number}</td>
              <td>{scan.extracted_set_code}</td>
              <td>{scan.confidence.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
