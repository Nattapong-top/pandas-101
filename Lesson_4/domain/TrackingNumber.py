from pydantic import BaseModel, Field, field_validator

class TrackingNumber(BaseModel):

    value: str = Field(..., min_length=1, json_schema_extra={'strip_whitespace': True})

    @field_validator('value')
    def check_length(cls, v):
        if len(v) < 5:
            raise ValueError('Tracking Number สั้นเกินไป')
        return v.strip()
    

if __name__ == "__main__":
    good_track = TrackingNumber(value='TH1234567890')
    print(f'สำเร็จ: ได้รับพัสดุ {good_track.value}')

    try:
        bad_track = TrackingNumber(value='TH12')
    except ValueError as e:
        print(f'โดนดัก error {e}')
