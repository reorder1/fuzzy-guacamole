'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Button, Table } from 'react-bootstrap';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface Score {
  id: number;
  raw_score: number;
  percent: number;
  set_code: string;
  student: {
    student_number: string;
    full_name: string;
  };
}

export default function ResultsPage() {
  const params = useParams<{ id: string }>();
  const examId = params.id;

  const query = useQuery({
    queryKey: ['scores', examId],
    queryFn: async () => {
      const res = await api.get('/scores/', { params: { exam: examId } });
      return res.data as Score[];
    }
  });

  const exportCsv = async () => {
    const res = await api.get(`/exams/${examId}/export/`, { responseType: 'blob' });
    const url = URL.createObjectURL(res.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `exam-${examId}-scores.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center">
        <h1>Results</h1>
        <Button onClick={exportCsv}>Export CSV</Button>
      </div>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Student #</th>
            <th>Name</th>
            <th>Set</th>
            <th>Raw Score</th>
            <th>Percent</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((score) => (
            <tr key={score.id}>
              <td>{score.student.student_number}</td>
              <td>{score.student.full_name}</td>
              <td>{score.set_code}</td>
              <td>{score.raw_score}</td>
              <td>{score.percent.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
