'use client';

import { useParams } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button, Form, Table } from 'react-bootstrap';
import { FormEvent, useState } from 'react';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface Student {
  id: number;
  student_number: string;
  full_name: string;
  email: string;
}

export default function StudentsPage() {
  const params = useParams<{ id: string }>();
  const batchId = params.id;
  const [studentNumber, setStudentNumber] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

  const query = useQuery({
    queryKey: ['students', batchId],
    queryFn: async () => {
      const res = await api.get('/students/', { params: { batch: batchId } });
      return res.data as Student[];
    }
  });

  const mutation = useMutation({
    mutationFn: async () => {
      await api.post('/students/', {
        batch: batchId,
        student_number: studentNumber,
        full_name: fullName,
        email
      });
    },
    onSuccess: () => {
      setStudentNumber('');
      setFullName('');
      setEmail('');
      query.refetch();
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <Layout>
      <h1>Students</h1>
      <Form onSubmit={handleSubmit} className="mb-4 d-flex gap-2">
        <Form.Control placeholder="Student Number" value={studentNumber} onChange={(e) => setStudentNumber(e.target.value)} required />
        <Form.Control placeholder="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        <Form.Control placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Button type="submit">Add</Button>
      </Form>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Student Number</th>
            <th>Name</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((student) => (
            <tr key={student.id}>
              <td>{student.student_number}</td>
              <td>{student.full_name}</td>
              <td>{student.email}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
