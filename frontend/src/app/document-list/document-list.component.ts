import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

type PreviousDoc = {
  filename: string;
  category: string;
  confidence: number;
  upload_time: string;
}

@Component({
  selector: 'document-list',
  imports: [CommonModule],
  templateUrl: './document-list.component.html',
  styleUrl: './document-list.component.css'
})
export class DocumentListComponent implements OnInit {
  data: PreviousDoc[] = [];
  loading: boolean = true;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData() {
    this.loading = true;
    const apiUrl = 'http://127.0.0.1:8000/get_documents';

    this.http.get<PreviousDoc[]>(apiUrl).subscribe({
      next: (data) => {
        this.data = data;
        this.loading = false;
      },
      error: (error) => {
        // TODO: Handle error
        console.error('Error fetching data:', error);
        this.loading = false; // Even on error, stop loading indicator
        // Handle the error appropriately, e.g., display an error message
      }
    });
  }
}
