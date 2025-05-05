from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from auth.auth_handler import extract_user_id
from sqlmodel import Session, select
from db.session import get_session
from schemas.models import Medium, Shell, Analysis, Core
from schemas.tasks import MetalData, OtherData, NewAnalysis
from analysis import get_permittivites, get_wavelength

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/data", tags=["Данные"])

@router.post("/shell", status_code=status.HTTP_201_CREATED,
             summary = 'Добавить данные по возможным оболочкам')
def create_shell(data: MetalData,
                 token: str = Depends(oauth2_scheme),
                 session: Session = Depends(get_session)):
    shell = session.query(Shell).filter(Shell.shell_name == data.material_name).first()
    if shell:
        raise HTTPException(status_code=422,
                            detail="Данный материал уже существует")
    shell = Shell(shell_name = data.material_name,
                  plasm_frequency = data.plasm_frequency,
                  gamma = data.gamma,
                  inf_permittivity = data.inf_permittivity,
                  shell_doi = data.doi,
                  user_id = int(extract_user_id(token)))
    session.add(shell)
    session.commit()
    session.refresh(shell)
    return {"message": "Материал успешно добавлен"}

@router.post("/core", status_code=status.HTTP_201_CREATED,
             summary = 'Добавить данные по возможным ядрам')
def create_core(data: OtherData,
                 token: str = Depends(oauth2_scheme),
                 session: Session = Depends(get_session)):
    core = session.query(Core).filter(Core.core_name == data.material_name).first()
    if core:
        raise HTTPException(status_code=422,
                            detail="Данный материал уже существует")
    core = Core(core_name = data.material_name,
                core_permittivity = data.permittivity,
                core_doi = data.doi,
                user_id = extract_user_id(token))
    session.add(core)
    session.commit()
    session.refresh(core)
    return core

@router.post("/medium", status_code=status.HTTP_201_CREATED,
             summary = 'Добавить данные по возможным средам')
def create_medium(data: OtherData,
                 token: str = Depends(oauth2_scheme),
                 session: Session = Depends(get_session)):
    medium = session.query(Medium).filter(Medium.medium_name == data.material_name).first()
    if medium:
        raise HTTPException(status_code=422,
                            detail="Данный материал уже существует")
    medium = Medium(medium_name = data.material_name,
                  medium_permittivity = data.permittivity,
                  medium_doi = data.doi,
                  user_id = extract_user_id(token))
    session.add(medium)
    session.commit()
    session.refresh(medium)
    return medium

@router.post("/analysis", status_code=status.HTTP_201_CREATED,
             summary = 'Отправить запрос на анализ')
def create_analysis(data: NewAnalysis,
                    token: str = Depends(oauth2_scheme),
                    session: Session = Depends(get_session)):
    core = session.query(Core).filter(Core.core_name == data.core_name).first()
    if core:
        core_i = core.core_id
        core_permittivity = core.core_permittivity
    else:
        raise HTTPException(status_code=404,
                            detail="материал для ядра не найден в базе данных")

    shell = session.query(Shell).filter(Shell.shell_name == data.shell_name).first()
    if shell:
        shell_i = shell.shell_id
        inf_permittivity = shell.inf_permittivity
        gamma = shell.gamma
        plasm_frequency = shell.plasm_frequency
    else:
        raise HTTPException(status_code=404,
                            detail="материал для оболочки не найден в базе данных")

    medium = session.query(Medium).filter(Medium.medium_name == data.medium_name).first()
    if medium:
        medium_i = medium.medium_id
        medium_permittivity = medium.medium_permittivity
    else:
        raise HTTPException(status_code=404,
                            detail="материал для среды не найден в базе данных")

    permittivites = get_permittivites(data.core_radius, data.radius,
                                      medium_permittivity, core_permittivity)
    analysis = Analysis(core_radius = data.core_radius,
                        radius = data.radius,
                        core_id = core_i,
                        shell_id = shell_i,
                        medium_id = medium_i,
                        first_resonance = get_wavelength(permittivites[0],
                                                         inf_permittivity,
                                                         gamma, plasm_frequency),
                        second_resonance= get_wavelength(permittivites[1],
                                                         inf_permittivity,
                                                         gamma, plasm_frequency),
                        first_transparency=get_wavelength(permittivites[2],
                                                          inf_permittivity,
                                                          gamma, plasm_frequency),
                        second_transparency=get_wavelength(permittivites[3],
                                                           inf_permittivity,
                                                           gamma, plasm_frequency),
                        user_id = extract_user_id(token))
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis

@router.get("/shell", status_code=status.HTTP_200_OK,
            summary = 'Получить таблицу оболочек')
def get_shell(session: Session = Depends(get_session)):
    shell = session.exec(select(Shell)).all()
    if shell is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return shell

@router.get("/core", status_code=status.HTTP_200_OK,
            summary = 'Получить таблицу ядер')
def get_core(session: Session = Depends(get_session)):
    core = session.exec(select(Core)).all()
    if core is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return core

@router.get("/medium", status_code=status.HTTP_200_OK,
            summary = 'Получить таблицу сред')
def get_medium(session: Session = Depends(get_session)):
    medium = session.exec(select(Medium)).all()
    if medium is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The task list is empty."
        )
    return medium

@router.get("/analysis", status_code=status.HTTP_200_OK,
            summary = 'Получить таблицу анализа')
def get_analysis(session: Session = Depends(get_session)):
    statement = (
        select(Analysis, Core, Shell, Medium)
        .join(Core, Analysis.core_id == Core.core_id)
        .join(Shell, Analysis.shell_id == Shell.shell_id)
        .join(Medium, Analysis.medium_id == Medium.medium_id)
    )
    results = session.exec(statement).all()
    return [
        {
            "id": analysis.analysis_id,
            "core_name": core.core_name,
            "shell_name": shell.shell_name,
            "medium_name": medium.medium_name,
            "radius": analysis.radius,
            "core_radius": analysis.core_radius,
            "first_resonance": analysis.first_resonance,
            "second_resonance": analysis.second_resonance,
            "first_transparency": analysis.first_transparency,
            "second_transparency": analysis.second_transparency
        }
        for analysis, core, shell, medium in results
    ]

@router.patch("/shell/{shell_name}", status_code=status.HTTP_200_OK,
              summary = 'Обновить данные по материалу оболочки')
def update_shell_by_name(shell_name: str,
                         data: MetalData, request: Request,
                         token: str = Depends(oauth2_scheme),
                         session: Session = Depends(get_session)):
    shell = session.query(Shell).filter(Shell.shell_name == shell_name).first()
    if shell is None:
        raise HTTPException(status_code=404,
                            detail="Данного материала не существует")

    setattr(shell, "shell_name", data.material_name)
    setattr(shell, "plasm_frequency", data.plasm_frequency)
    setattr(shell, "inf_permittivity", data.inf_permittivity)
    setattr(shell, "gamma", data.gamma)
    setattr(shell, "shell_doi", data.material_name)
    setattr(shell, "user_id", int(extract_user_id(token)))
    session.commit()
    session.refresh(shell)
    return shell

@router.patch("/core/{core_name}", status_code=status.HTTP_200_OK,
              summary = 'Изменить таблицу ядер')
def update_core_by_name(core_name: str,
                         data: OtherData, request: Request,
                         token: str = Depends(oauth2_scheme),
                         session: Session = Depends(get_session)):
    core = session.query(Core).filter(Core.core_name == core_name).first()
    if core is None:
        raise HTTPException(status_code=404,
                            detail="Данного материала не существует")

    setattr(core, "core_name", data.material_name)
    setattr(core, "core_permittivity", data.permittivity)
    setattr(core, "core_doi", data.doi)
    setattr(core, "user_id", int(extract_user_id(token)))
    session.commit()
    session.refresh(core)
    return core

@router.patch("/medium/{medium_name}", status_code=status.HTTP_200_OK,
              summary = 'Изменить таблицу среды')
def update_medium_by_name(medium_name: str,
                         data: OtherData, request: Request,
                         token: str = Depends(oauth2_scheme),
                         session: Session = Depends(get_session)):
    medium = session.query(Medium).filter(Medium.medium_name == medium_name).first()
    if medium is None:
        raise HTTPException(status_code=404,
                            detail="Данного материала не существует")

    setattr(medium, "medium_name", data.material_name)
    setattr(medium, "core_permittivity", data.permittivity)
    setattr(medium, "medium_doi", data.doi)
    setattr(medium, "user_id", int(extract_user_id(token)))
    session.commit()
    session.refresh(medium)
    return medium

@router.delete("/analysis/{analysis_id}", status_code=status.HTTP_200_OK,
               summary = 'Удалить строки анализа')
def delete_analysis_by_id(analysis_id: int,
                          token: str = Depends(oauth2_scheme),
                          session: Session = Depends(get_session)):
    statement = select(Analysis).where(Analysis.analysis_id == analysis_id)
    analysis = session.exec(statement).one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404,
                            detail="такой строки не существует")
    else:
        session.delete(analysis)
        session.commit()
        return {"message": "выбранная строка успешно удалена"}