import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ZPageNotFoundComponent } from './z-page-not-found.component';

describe('ZPageNotFoundComponent', () => {
  let component: ZPageNotFoundComponent;
  let fixture: ComponentFixture<ZPageNotFoundComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ZPageNotFoundComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ZPageNotFoundComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
