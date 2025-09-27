'use client';

import { useQuery } from '@tanstack/react-query';
import { Table } from 'react-bootstrap';
import Link from 'next/link';
import Layout from '../../components/Layout';
import { api } from '../../lib/api';

interface Exam {
  id: number;
  title: string;
  num_items: number;
  batch: number;
  sets: { id: number; set_code: string }[];
}

export default function ExamsIndexPage() {
  const query = useQuery({
    queryKey: ['exams'],
    queryFn: async () => {
      const res = await api.get('/exams/');
      return res.data as Exam[];
    }
  });

  return (
    <Layout>
      <h1>All Exams</h1>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Title</th>
            <th>Items</th>
            <th>Sets</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((exam) => (
            <tr key={exam.id}>
              <td>{exam.title}</td>
              <td>{exam.num_items}</td>
              <td>{exam.sets?.map((set) => set.set_code).join(', ')}</td>
              <td>
                <Link href={`/exams/${exam.id}/results`}>Results</Link>
                {' | '}
                <Link href={`/exams/${exam.id}/analytics`}>Analytics</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
