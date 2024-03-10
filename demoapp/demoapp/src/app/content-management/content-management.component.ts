import { Component, OnInit, Input } from '@angular/core';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-content-management',
  templateUrl: './content-management.component.html',
  styleUrls: ['./content-management.component.css']
})
export class ContentManagementComponent implements OnInit {
  constructor(private sanitizer: DomSanitizer) { }

  // Private variable to hold custom data
  private _customData: any[] = [];

  /**
   * Setter for custom data
   * @param {any[]} value - The new value for custom data
   */
  @Input()
  set customData(value: any[]) {
    if (Array.isArray(value)) {
      this._customData = value;
      this.allItems = this._customData;
      this.totalPages = Math.ceil(this.allItems.length / this.itemsPerPage);
      this.currentPage = 1;
      this.items = this.getItemsForPage(this.currentPage);
      this.totalImages = this.allItems.length
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages;
      }
    }
  }

  /**
   * Getter for custom data
   * @returns {any[]} The current value of custom data
   */
  get customData(): any[] {
    return this._customData;
  }

  // Variables to hold items and statuses
  allItems: any[] = [];
  items: any[] = [];
  statuses = ['Waiting for review', 'Approved', 'Rejected'];

  // Variables for pagination
  itemsPerPage = 4;
  currentPage = 0;
  totalPages = 0;
  totalImages = 0

  /**
   * Go to the previous page
   */
  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.items = this.getItemsForPage(this.currentPage);
    }
  }

  /**
   * Go to the next page
   */
  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.items = this.getItemsForPage(this.currentPage);
    }
  }

  /**
   * Get items for a specific page
   * @param {number} page - The page number
   * @returns {any[]} The items for the specified page
   */
  getItemsForPage(page: number) {
    const start = (page - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.allItems.slice(start, end);
  }

  /**
   * Angular lifecycle hook that is called after data-bound properties of a directive are initialized
   */
  ngOnInit(): void {
    if (Array.isArray(this.customData)) {
      this.allItems = this.customData;
      this.items = this.getItemsForPage(this.currentPage);
      this.totalPages = Math.ceil(this.allItems.length / this.itemsPerPage);
    }
  }
}
