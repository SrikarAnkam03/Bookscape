import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.css']
})
export class AlertComponent implements OnChanges {
  @Input() message: string | null = null;
  alerts: string[] = [];
  ngOnChanges(changes: SimpleChanges) {
    if (changes['message'] && this.message) {
      this.alerts.push(this.message); 
 
      setTimeout(() => {
        this.alerts.shift(); 
      }, 3000);
    }
  }
}
