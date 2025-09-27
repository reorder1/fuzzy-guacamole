'use client';

import { useParams, useRouter } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button, Form, Table } from 'react-bootstrap';
import { FormEvent, useState } from 'react';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface Exam {
  id: number;
  title: string;
  num_items: number;
}

export default function ExamsPage() {
  const params = useParams<{ id: string }>();
  const batchId = params.id;
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [numItems, setNumItems] = useState(100);

  const query = useQuery({
    queryKey: ['exams', batchId],
    queryFn: async () => {
      const res = await api.get('/exams/', { params: { batch: batchId } });
      return res.data as Exam[];
    }
  });

  const mutation = useMutation({
    mutationFn: async () => {
      await api.post('/exams/', { batch: batchId, title, num_items: numItems });
    },
    onSuccess: () => {
      setTitle('');
      query.refetch();
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <Layout>
      <h1>Exams</h1>
      <Form onSubmit={handleSubmit} className="mb-4 d-flex gap-2">
        <Form.Control placeholder="Exam title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <Form.Control
          placeholder="Items"
          type="number"
          value={numItems}
          min={1}
          onChange={(e) => setNumItems(Number(e.target.value))}
        />
        <Button type="submit">Add</Button>
      </Form>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Title</th>
            <th>Items</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((exam) => (
            <tr key={exam.id}>
              <td>{exam.title}</td>
              <td>{exam.num_items}</td>
              <td className="d-flex gap-2">
                <Button size="sm" onClick={() => router.push(`/exams/${exam.id}/keys`)}>
                  Answer Keys
                </Button>
                <Button size="sm" onClick={() => router.push(`/exams/${exam.id}/upload`)}>
                  Upload Scans
                </Button>
                <Button size="sm" onClick={() => router.push(`/exams/${exam.id}/review`)}>
                  Review Queue
                </Button>
                <Button size="sm" onClick={() => router.push(`/exams/${exam.id}/results`)}>
                  Results
                </Button>
                <Button size="sm" onClick={() => router.push(`/exams/${exam.id}/analytics`)}>
                  Analytics
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
